import base64
from dotenv import dotenv_values
import requests

config = {
    **dotenv_values('.env'),
    **dotenv_values('.env.local'),
}


class SpotifyClient:
    pass

    def __init__(self, **kwargs):
        self.primary_device_id = None
        self.access_token = kwargs['access_token']
        self.refresh_token = kwargs['refresh_token']
        self.current_player_is_playing = False

    def get(self, *args):
        url = args[0]
        response = requests.get(
            f'https://api.spotify.com{url}',
            headers={
                'Authorization': f'Bearer {self.access_token}'
            }
        )
        if response.status_code == 401:  # The access token expired
            self.refresh_token()
            response = requests.get(
                f'https://api.spotify.com{url}',
                headers={
                    'Authorization': f'Bearer {self.access_token}'
                }
            )

        print(response.json())
        return response.json()

    def put(self, *args):
        url = args[0]
        response = requests.put(
            f'https://api.spotify.com{url}',
            headers={
                'Authorization': f'Bearer {self.access_token}'
            }
        )
        if response.status_code == 401:  # The access token expired
            self.refresh_token()
            response = requests.put(
                f'https://api.spotify.com{url}',
                headers={
                    'Authorization': f'Bearer {self.access_token}'
                }
            )

        print(response)
        return response

    def refresh_token(self):
        client_id = config['VUE_APP_SPOTIFY_CLIENT_ID']
        client_secret = config['VUE_APP_SPOTIFY_CLIENT_SECRET']
        encoded = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode("ascii")
        response = requests.post(
            'https://api.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            },
            headers={
                'Authorization': f'Basic {encoded}'
                #                                 'Authorization': f'Bearer {self.access_token}'
            }
        )
        data = response.json()
        self.access_token = data['access_token']
        pass

    def get_devices(self):
        if self.primary_device_id is None:
            data = self.get(
                '/v1/me/player/devices'
            )
            primary_device = next(filter(lambda device: device['type'] == 'Speaker', data['devices']), None)
            print(primary_device['id'])
            self.primary_device_id = primary_device['id']

    def play_or_pause(self):
        self.fetch_player()
        if self.current_player_is_playing:
            self.pause()
        else:
            self.play()

    def play(self):
        url = '/v1/me/player/play'
        if self.primary_device_id is not None:
            url += f'?device_id={self.primary_device_id}'
        self.current_player_is_playing = True
        response = self.put(url)

    def pause(self):
        self.current_player_is_playing = False
        self.put('/v1/me/player/pause')

    def fetch_player(self):
        data = self.get('/v1/me/player')
        if data['is_playing']:
            self.current_player_is_playing = True
        else:
            self.current_player_is_playing = False

    def oauth(self):
        pass
