import os
import sys
import json
import socket
import asyncio
from aiohttp import web, WSMsgType

app = web.Application()

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
	print("New socket")

	ws.send_json({"type": "init"});
	async for msg in ws:
		# Ignore non-JSON messages
		if msg.type != WSMsgType.TEXT: continue
		try: msg = json.loads(msg.data)
		except ValueError: continue
		print("MESSAGE", msg)

	await ws.close()
	print("Gone")
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
