from typing import List

from dotenv import load_dotenv
import os
import requests
import json
from urllib.parse import urlencode

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
token_url = 'https://id.twitch.tv/oauth2/token'
access_user = 'https://id.twitch.tv/oauth2/authorize'
redirect_uri = "http://localhost:3000"


class TwitchAPI:

    def __init__(self, client_id, client_secret):
        self.headers = None
        self.expires_in = None
        self.connected_chats: List | None = None
        self.client_id = client_id
        self.client_secret = client_secret

        # user acess
        self.refresh_token = None

    def ref_token(self, refresh_token=None):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        try:
            # response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
            response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to retrieve access token: {params}")
            print(response.status_code)
            print(response.json())
            return None
        except requests.exceptions.RequestException as err:
            print(f"Failed to retrieve access token: {params}")
            print(response.status_code)
            print(response.json())
            return None

        print(response.json())
        bearer = response.json()['access_token']
        self.refresh_token = response.json()["refresh_token"]
        self.headers = {
            'Authorization': f'Bearer {bearer}',
            'Client-Id': self.client_id,
        }

    def make_user_auth(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "user:read:chat"
        }
        query_string = urlencode(params)

        # Construct the full URL
        auth_url = f"{access_user}?{query_string}"

        print(auth_url)
        return auth_url

    def auth_user(self, code):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        # data = f'client_id={self.client_id}&client_secret={self.client_secret}&code={code}&grant_type=authorization_code&redirect_uri={redirect_uri}'
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        try:
            # response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
            response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to retrieve access token: {params}")
            print(response.status_code)
            print(response.json())
            return None
        except requests.exceptions.RequestException as err:
            print(f"Failed to retrieve access token: {params}")
            print(response.status_code)
            print(response.json())
            return None

        bearer = response.json()['access_token']
        self.expires_in = response.json()["expires_in"]
        self.refresh_token = response.json()["refresh_token"]
        self.headers = {
            'Authorization': f'Bearer {bearer}',
            'Client-Id': self.client_id,
        }

    def auth(self, client_id, client_secret):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = f'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'

        try:
            response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to retrieve access token: {data}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Failed to retrieve access token: {data}")
            return None

        bearer = response.json()['access_token']
        self.expires_in = response.json()["expires_in"]
        self.headers = {
            'Authorization': f'Bearer {bearer}',
            'Client-Id': client_id,
        }

    def get_user_info(self, channel_name: str):
        url = 'https://api.twitch.tv/helix/users'
        response = requests.get(url, headers=self.headers, params={'login': channel_name})
        return response.json()

    def get_streams(self, channel_id):
        pass

    def connect_to_chat(self):
        ws_nossl = "ws://irc-ws.chat.twitch.tv:80"


# step by step
"""
# If app access token
1. run the auth()
2. use updated header, when expires call auth again 

# IF user access token
1. generate link for a user using make_user_auth()
if user authorizes example correct link http://localhost:3000/?code= 96le3w4pitvopv1f60000000000 &scope=user%3Aread%3Achat
2. user authorizes app, somehow get from him  the code
3. run the auth_user with that code. 
4. if expires use REFRESH_TOKEN you can't use make_user_auth(), unless user returns new code.
"""

if __name__ == '__main__':

    twitch_api = TwitchAPI(CLIENT_ID, CLIENT_SECRET)
    # twitch_api.auth(CLIENT_ID, CLIENT_SECRET)
    # twitch_api.make_user_auth()
    # code = "code"
    # twitch_api.auth_user(code)
    twitch_api.ref_token("ref_token")
    print(twitch_api.headers)
    print(twitch_api.refresh_token)

