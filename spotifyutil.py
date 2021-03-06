import requests
import base64
import random
import string
import urllib
import urllib.parse
from http.server import BaseHTTPRequestHandler
from dotenv import dotenv_values

import spotifyclient

config = {
    **dotenv_values('.env'),
    **dotenv_values('.env.local'),
}
from oauthlib.oauth2 import WebApplicationClient


def random_name(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(n)])


class CallbackServer(BaseHTTPRequestHandler):
    g_oauth_state = None
    g_access_token = None
    g_refresh_token = None

    spotify_client = None
#    primary_device_id = None

    VUE_APP_SPOTIFY_CLIENT_ID = config['VUE_APP_SPOTIFY_CLIENT_ID']
    VUE_APP_SPOTIFY_CLIENT_SECRET = config['VUE_APP_SPOTIFY_CLIENT_SECRET']

    def __init__(self, *args):
        print(f'CallbackServer::init start {args}')
        BaseHTTPRequestHandler.__init__(self, *args)
        print('CallbackServer::init finish')

    def callback_method(self, path, query, redirect_uri):
        print(f'path={path}, query = {query}')

        if path == '/callback':
            params = urllib.parse.parse_qs(query)
            print('CODE')
            print(params['code'][0])
            print('STATE')
            print(f'g_oauth_state = {self.g_oauth_state}')
            print(params['state'][0])
            print(self.g_oauth_state)
            if CallbackServer.g_oauth_state == params['state'][0]:
                print('OK!')
                data = {
                    'code': params['code'][0],
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                }
                encoded = base64.b64encode(
                    f'{CallbackServer.VUE_APP_SPOTIFY_CLIENT_ID}:{CallbackServer.VUE_APP_SPOTIFY_CLIENT_SECRET}'.encode(
                        'utf-8')).decode("ascii")
                print(encoded)
                print(redirect_uri)
                response = requests.post(
                    'https://accounts.spotify.com/api/token',
                    data=data,
                    headers={
                        'Authorization': f'Basic {encoded}'
                    }
                )
                print(response)
                print(response.text)
                # print(response.json())
                res_data = response.json()
                CallbackServer.spotify_client = spotifyclient.SpotifyClient(
                    access_token=res_data['access_token'],
                    refresh_token=res_data['refresh_token']
                )
                CallbackServer.g_access_token = res_data['access_token']
                CallbackServer.g_refresh_token = res_data['refresh_token']
                return 'oauth OK!'
            else:
                return 'oauth NG!'

        return ['Hello', 'World!', 'with', query]

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        print(self.headers['Host'])
        print(self.path)
        print(parsed_path)
        print(parsed_path.path)
        path = parsed_path.path
        query = parsed_path.query

        host = self.headers['Host']
        redirect_uri = f'http://{host}/callback'

        if query == 'oauth':
            scope = [
                'user-library-read',
                'user-modify-playback-state',
                'user-read-email',
                'user-read-playback-state',
                'user-read-private',
                'user-read-recently-played'
            ]
            state = random_name(16)
            CallbackServer.g_oauth_state = state
            print(f'g_oauth_state = {CallbackServer.g_oauth_state}')
            oauth = WebApplicationClient(CallbackServer.VUE_APP_SPOTIFY_CLIENT_ID)
            url, headers, body = oauth.prepare_authorization_request('https://accounts.spotify.com/authorize',
                                                                     redirect_url=redirect_uri,
                                                                     scope=scope,
                                                                     state=state)

            self.send_response(302)
            self.send_header('Location', url)
            self.end_headers()
            return

        elif path == '/callback':
            result = self.callback_method(parsed_path.path, query, redirect_uri)
            self.send_response(302)
            self.send_header('Location', '/spotify1')
            self.end_headers()
            #            self.end_headers()
            #            message = result
            #            self.wfile.write(message.encode('utf-8'))
            return

        elif path == '/spotify1':
            CallbackServer.spotify_client.get(
                '/v1/me/player/devices'
            )
            self.send_response(200)
            self.end_headers()
            message = 'devices'
            self.wfile.write(message.encode('utf-8'))
            return



        else:
            self.send_response(200)
            self.end_headers()
            message = query
            self.wfile.write(message.encode('utf-8'))
            return

    def ir1(self, name):
        print(f'ir1 {name}')
        CallbackServer.spotify_client.get_devices()
        CallbackServer.spotify_client.play_or_pause()

    def play(self):

        pass
