import http.server
from http.server import HTTPServer

import spotifyutil

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

g_server = None


def start(port):
    def handler(*args):
        global g_server
        g_server = spotifyutil.CallbackServer(*args)

    server = HTTPServer(('', int(port)), handler)
    server.serve_forever()


start(PORT)
