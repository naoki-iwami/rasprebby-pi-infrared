import time
import http.server
from http.server import HTTPServer

import spotifyutil
import irutil
import threading
import requests

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

g_server = None


def start(port):
    def handler(*args):
        global g_server
        print('start handler 1')
        g_server = spotifyutil.CallbackServer(*args)
        print(f'start handler {g_server}')

    server = HTTPServer(('', int(port)), handler)

    print('START serve_forever()')
    server.serve_forever()
    print('FINISH serve_forever()')


def start_web_server():
    start(PORT)

def ir_callback(name):
    global g_server
    print(f'ir_callback {name}')
    if name == 'r_center':
        print('key = r_center')
        g_server.ir1(name)


def start_ir_server():
    print('start_ir_server()')
    ir_server = irutil.InfraredServer(ir_callback)
    ir_server.start()

# start_web_server()
# start_ir_server()

thread1 = threading.Thread(target=start_web_server)
thread2 = threading.Thread(target=start_ir_server)

print('STEP 0')
thread1.start()
print('STEP 1')
thread2.start()
print('STEP 2')

#time.sleep(0.1)
#response = requests.get('http://localhost:8000/?oauth')
#print(response.status_code)
# print(response.text)
#print(response.headers['Location'])

#response = requests.get(response.headers['Location'])
#print(response.status_code)
#print(response.text)
# print(response.headers)


time.sleep(0.1)
response = requests.get('http://localhost:8000/healthcheck')
print(response)

thread1.join()
print('STEP 3')
thread2.join()
print('STEP 4')

