import os
import re
import sys
import json
import socket
import asyncio
from aiohttp import web, WSMsgType

app = web.Application()
rooms = {}

class Room:
	# Color names taken from https://en.wikipedia.org/wiki/Template:Monopoly_board_layout
	# including the variant that the cheapest ones are Indigo, not SaddleBrown
	property_data = """
	Indigo/White: 60/60 Old Kent, Whitechapel
	SkyBlue: 100/120 Angel Islington, Euston, Pentonville
	DarkOrchid/White: 140/160 Pall Mall, Whitehall, Northumberland
	Orange: 180/200 Bow, Marlborough, Vine
	Red: 220/240 Strand, Fleet, Trafalgar
	Yellow: 260/280 Leicester, Coventry, Piccadilly
	Green/White: 300/320 Regent, Oxford, Bond
	Blue/White: 350/400 Park Lane, Mayfair
	Black/White: 200/200 King's Cross, Marylebone, Fenchurch, Liverpool
	White: 150/150 Electric, Water Works
	"""

	def __init__(self, id):
		if os.environ.get("WS_KEEPALIVE"):
			asyncio.ensure_future(self.keepalive())
		self.clients = []
		self.proporder = []
		self.funds = 1500 # Everyone's initial spendable money
		self.id = id; rooms[self.id] = self # floop
		print("Creating new room %s [%d rooms]" % (self.id, len(rooms)))
		self.dying = None # Set to true when we run out of clients
		self.all_done = False

		# Preprocess the property data into a more useful form.
		self.properties = {}
		for group in self.property_data.splitlines():
			group = group.strip()
			if not group: continue
			color, price1, price2, names = re.match("([A-Za-z/]+): ([0-9]+)/([0-9]+) (.*)", group).groups()
			names = names.split(", ")
			if "/" in color: color, fg = color.split("/")
			else: fg = "Black"
			for name in names:
				self.proporder.append(name)
				self.properties[name] = {"facevalue": int(price1), "color": color, "fg": fg}
			# Alter the price of the last one (the top one of the group)
			self.properties[name]["facevalue"] = int(price2)

	def send_users(self):
		"""Notify all clients of updated public user data"""
		users = {ws.username: self.funds for ws in self.clients if ws.username}
		for prop in self.properties.values():
			if "bidder" in prop:
				users[prop["bidder"]] -= prop["highbid"]
		info = {"type": "users",
			"done_count": sum(ws.done for ws in self.clients if ws.username),
			"all_done": self.all_done,
			"users": sorted(users.items()),
		}
		for ws in self.clients:
			ws.funds = info["funds"] = users.get(ws.username, self.funds)
			info["done"] = ws.done
			ws.send_json(info)

	async def ws_login(self, ws, name, **xtra):
		if ws.username: return None
		ws.username = str(name)[:32]
		ws.send_json({"type": "login", "name": ws.username})
		self.send_users()

	async def ws_done(self, ws, **xtra):
		ws.done = True
		for cli in self.clients:
			if not ws.done: break
		else:
			# Everyone's done. Mode switch!
			self.all_done = True
		self.send_users()

	async def ws_bid(self, ws, name, value, **xtra):
		if self.all_done: return None
		prop = self.properties[name]
		value = int(value)
		minbid = prop["facevalue"] if "bidder" not in prop else prop["highbid"] + 10
		if value < minbid: return None
		if value > ws.funds: return None
		prop["highbid"] = value
		prop["bidder"] = ws.username
		for cli in self.clients: cli.done = False
		self.send_users()
		return {"type": "property", "name": name, "data": prop}

	async def keepalive(self):
		"""Keep the websockets alive

		In some environments, we lose any inactive websockets. So keep telling
		them about users - that's safe, at least.
		"""
		while True:
			await asyncio.sleep(30)
			self.send_users()

	async def websocket(self, ws, login_data):
		ws.username = None; ws.done = False
		self.dying = None # Whenever anyone joins, even if they disconnect fast, reset the death timer.
		self.clients.append(ws)
		await self.ws_login(ws, **login_data)
		print("New socket in %s (now %d)" % (self.id, len(self.clients)))

		ws.send_json({"type": "properties", "data": self.properties, "order": self.proporder});
		async for msg in ws:
			# Ignore non-JSON messages
			if msg.type != WSMsgType.TEXT: continue
			try: msg = json.loads(msg.data)
			except ValueError: continue
			print("MESSAGE", msg)
			if "type" not in msg or "data" not in msg: continue
			f = getattr(self, "ws_" + msg["type"], None)
			if not f: continue
			try:
				resp = await f(ws, **msg["data"])
			except Exception as e:
				print("Exception in ws handler:")
				print(e)
				continue
			if resp is None: continue
			for client in self.clients:
				client.send_json(resp)

		self.clients.remove(ws)
		await ws.close()
		print("Socket gone from %s (%d left)" % (self.id, len(self.clients)))
		if not self.clients:
			asyncio.ensure_future(self.die())
		return ws

	async def die(self):
		"""Destroy this room after a revive delay"""
		sentinel = object()
		self.dying = sentinel
		print("Room %s dying" % self.id)
		await asyncio.sleep(60)
		if self.dying is sentinel:
			# If it's not sentinel, we got revived. Maybe the
			# other connection is in dying mode, maybe not;
			# either way, we aren't in charge of death.
			assert not self.clients
			del rooms[self.id]
			print("Room %s dead - %d rooms left" % (self.id, len(rooms)))
		else:
			if self.dying:
				print("Room %s revived-but-still-dying" % self.id)
			else:
				print("Room %s revived" % self.id)

def route(url):
	def deco(f):
		app.router.add_get(url, f)
		return f
	return deco

@route("/")
async def home(req):
	with open("build/index.html") as f:
		return web.Response(text=f.read(), content_type="text/html")

@route("/ws")
async def websocket(req):
	ws = web.WebSocketResponse()
	await ws.prepare(req)
	async for msg in ws:
		if msg.type != WSMsgType.TEXT: continue
		try:
			msg = json.loads(msg.data)
			if msg["type"] != "login": continue
			room = msg["data"]["room"][:32]
			if room: break
		except (ValueError, KeyError, TypeError):
			# Any parsing error, just wait for another message
			continue
	else:
		# Something went wrong with the handshake. Kick
		# the client and let them reconnect.
		await ws.close()
		return ws
	if room not in rooms: Room(room)
	return await rooms[room].websocket(ws, msg["data"])

# After all the custom routes, handle everything else by loading static files.
app.router.add_static("/", path="build", name="static")

# Lifted from appension
async def serve_http(loop, port, sock=None):
	if sock:
		srv = await loop.create_server(app.make_handler(), sock=sock)
	else:
		srv = await loop.create_server(app.make_handler(), "0.0.0.0", port)
		sock = srv.sockets[0]
	print("Listening on %s:%s" % sock.getsockname(), file=sys.stderr)

def run(port=8080, sock=None):
	loop = asyncio.get_event_loop()
	loop.run_until_complete(serve_http(loop, port, sock))
	# TODO: Announce that we're "ready" in whatever way
	try: loop.run_forever()
	except KeyboardInterrupt: pass

if __name__ == '__main__':
	# Look for a socket provided by systemd
	sock = None
	try:
		pid = int(os.environ.get("LISTEN_PID", ""))
		fd_count = int(os.environ.get("LISTEN_FDS", ""))
	except ValueError:
		pid = fd_count = 0
	if pid == os.getpid() and fd_count >= 1:
		# The PID matches - we've been given at least one socket.
		# The sd_listen_fds docs say that they should start at FD 3.
		sock = socket.socket(fileno=3)
		print("Got %d socket(s)" % fd_count, file=sys.stderr)
	run(port=int(os.environ.get("PORT", "8080")), sock=sock)
