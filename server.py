import os
import sys
import json
import socket
import asyncio
from aiohttp import web, WSMsgType

app = web.Application()

# TODO: Get the initial data from an external file
# TODO: Allow multiple simultaneous auctions by having a dict of room IDs to these.
properties = {
	"Vine Street": {"facevalue": 180, "color": "#E0A000"},
	"Mayfair": {"facevalue": 400, "color": "#000090", "fg": "white"},
}
clients = []
proporder = list(properties) # Assumes v. recent Python. If not, establish this another way.

def route(url):
	def deco(f):
		app.router.add_get(url, f)
		return f
	return deco

@route("/")
async def home(req):
	with open("build/index.html") as f:
		return web.Response(text=f.read(), content_type="text/html")

async def ws_bid(ws, name, value, **xtra):
	prop = properties[name]
	value = int(value)
	minbid = prop["facevalue"] if "bidder" not in prop else prop["highbid"] + 10
	if value < minbid: return None
	prop["highbid"] = value
	prop["bidder"] = "User"
	return {"type": "property", "name": name, "data": prop}

@route("/ws")
async def websocket(req):
	ws = web.WebSocketResponse()
	await ws.prepare(req)
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
