import os
import re
import sys
import json
import socket
import asyncio
from aiohttp import web, WSMsgType

app = web.Application()

# TODO: Get the initial data from an external file
# TODO: Allow multiple simultaneous auctions by having a dict of room IDs to these.
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
clients = []
proporder = []
funds = 1500 # Everyone's initial spendable money

# Preprocess the property data into a more useful form.
properties = {}
for group in property_data.splitlines():
	if not group: continue
	color, price1, price2, names = re.match("([A-Za-z/]+): ([0-9]+)/([0-9]+) (.*)", group).groups()
	names = names.split(", ")
	if "/" in color: color, fg = color.split("/")
	else: fg = "Black"
	for name in names:
		proporder.append(name)
		properties[name] = {"facevalue": int(price1), "color": color, "fg": fg}
	# Alter the price of the last one (the top one of the group)
	properties[name]["facevalue"] = int(price2)

def route(url):
	def deco(f):
		app.router.add_get(url, f)
		return f
	return deco

@route("/")
async def home(req):
	with open("build/index.html") as f:
		return web.Response(text=f.read(), content_type="text/html")

def send_users():
	"""Notify all clients of updated public user data"""
	users = {ws.username: funds for ws in clients if ws.username}
	for prop in properties.values():
		if "bidder" in prop:
			users[prop["bidder"]] -= prop["highbid"]
	info = {"type": "users", "users": sorted(users.items())}
	for ws in clients:
		ws.funds = info["funds"] = users.get(ws.username, funds)
		ws.send_json(info)

async def ws_login(ws, name, **xtra):
	if ws.username: return None
	ws.username = str(name)[:32]
	ws.send_json({"type": "login", "name": ws.username})
	send_users()

async def ws_bid(ws, name, value, **xtra):
	prop = properties[name]
	value = int(value)
	minbid = prop["facevalue"] if "bidder" not in prop else prop["highbid"] + 10
	if value < minbid: return None
	if value > ws.funds: return None
	prop["highbid"] = value
	prop["bidder"] = ws.username
	send_users()
	return {"type": "property", "name": name, "data": prop}

async def keepalive():
	"""Keep the websockets alive

	In some environments, we lose any inactive websockets. So keep telling
	them about users - that's safe, at least.
	"""
	while True:
		await asyncio.sleep(30)
		send_users()

@route("/ws")
async def websocket(req):
	ws = web.WebSocketResponse()
	await ws.prepare(req)
	ws.username = None
	clients.append(ws)
	print("New socket (now %d)" % len(clients))

	ws.send_json({"type": "properties", "data": properties, "order": proporder});
	async for msg in ws:
		# Ignore non-JSON messages
		if msg.type != WSMsgType.TEXT: continue
		try: msg = json.loads(msg.data)
		except ValueError: continue
		print("MESSAGE", msg)
		if "type" not in msg or "data" not in msg: continue
		if "ws_" + msg["type"] not in globals(): continue
		try:
			resp = await globals()["ws_" + msg["type"]](ws, **msg["data"])
		except Exception as e:
			print("Exception in ws handler:")
			print(e)
			continue
		if resp is None: continue
		for client in clients:
			client.send_json(resp)

	clients.remove(ws)
	await ws.close()
	print("Socket gone (%d left)" % len(clients))
	return ws

# After all the custom routes, handle everything else by loading static files.
app.router.add_static("/", path="build", name="static")

# Lifted from appension
async def serve_http(loop, port, sock=None):
	if sock:
		# NAUGHTY: Shouldn't do this. What's the documented way? I dunno.
		sock.setblocking(False)
		loop._start_serving(app.make_handler(), sock)
	else:
		srv = await loop.create_server(app.make_handler(), "0.0.0.0", port)
		sock = srv.sockets[0]
	print("Listening on %s:%s" % sock.getsockname(), file=sys.stderr)

def run(port=8080, sock=None):
	loop = asyncio.get_event_loop()
	loop.run_until_complete(serve_http(loop, port, sock))
	# TODO: Announce that we're "ready" in whatever way
	if os.environ.get("WS_KEEPALIVE"):
		asyncio.ensure_future(keepalive())
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
