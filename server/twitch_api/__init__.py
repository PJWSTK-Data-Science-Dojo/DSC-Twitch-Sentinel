import asyncio
from collections import deque
from typing import List, Set
from utils import Message
from dotenv import load_dotenv
import os
import requests
import json
from urllib.parse import urlencode

import websockets

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BOT_USERNAME = os.getenv("BOT_USERNAME")
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES"))

token_url = "https://id.twitch.tv/oauth2/token"
access_user = "https://id.twitch.tv/oauth2/authorize"
redirect_uri = "http://localhost:3000"


class TwitchAPI:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = None
        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.ws_url = "wss://irc-ws.chat.twitch.tv:443"
        self.websocket = None
        self.chat_task = None
        self.connected_chats: dict[str, deque] = {}
        self.name_to_id: dict[str, str] = {}
        self.id_to_name: dict[str, str] = {}

    async def start(self):
        """Start the Twitch chat connection in the background."""
        # Authenticate before starting the chat connection
        await self.authenticate()

        # Create an asyncio task for the chat connection
        self.chat_task = asyncio.create_task(self.chat())
        print("Twitch chat connection started.")

    async def authenticate(self):
        """Authenticate with Twitch and obtain an access token."""
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post("https://id.twitch.tv/oauth2/token", params=params)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.expires_in = token_data["expires_in"]
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Client-Id": self.client_id,
        }
        print("Authenticated with Twitch API.")

    def ref_token(self, refresh_token=None):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        try:
            # response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
            response = requests.post(
                "https://id.twitch.tv/oauth2/token", headers=headers, params=params
            )
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
        bearer = response.json()["access_token"]
        self.refresh_token = response.json()["refresh_token"]
        self.headers = {
            "Authorization": f"Bearer {bearer}",
            "Client-Id": self.client_id,
        }

    def make_user_auth(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "user:read:chat",
        }
        query_string = urlencode(params)

        # Construct the full URL
        auth_url = f"{access_user}?{query_string}"

        print(auth_url)
        return auth_url

    def auth_user(self, code):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        # data = f'client_id={self.client_id}&client_secret={self.client_secret}&code={code}&grant_type=authorization_code&redirect_uri={redirect_uri}'
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        try:
            # response = requests.post('https://id.twitch.tv/oauth2/token', headers=headers, data=data)
            response = requests.post(
                "https://id.twitch.tv/oauth2/token", headers=headers, params=params
            )
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

        bearer = response.json()["access_token"]
        self.expires_in = response.json()["expires_in"]
        self.refresh_token = response.json()["refresh_token"]
        self.headers = {
            "Authorization": f"Bearer {bearer}",
            "Client-Id": self.client_id,
        }

    def auth(self, client_id, client_secret):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"

        try:
            response = requests.post(
                "https://id.twitch.tv/oauth2/token", headers=headers, data=data
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to retrieve access token: {data}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Failed to retrieve access token: {data}")
            return None

        bearer = response.json()["access_token"]
        self.expires_in = response.json()["expires_in"]
        self.headers = {
            "Authorization": f"Bearer {bearer}",
            "Client-Id": client_id,
        }

    def get_user_info(self, channel_name: str):
        url = "https://api.twitch.tv/helix/users"
        response = requests.get(
            url, headers=self.headers, params={"login": channel_name}
        )
        return response.json()

    def get_streams_name(self, channel_name):
        url = "https://api.twitch.tv/helix/streams"
        params = {"user_login": channel_name, "type": "live"}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_streamer_login(self, channel_id):
        url = "https://api.twitch.tv/helix/streams"
        params = {"user_id": channel_id, "type": "live"}
        response = requests.get(url, headers=self.headers, params=params)
        data = response.json()
        if not data.get("data"):
            return None

        return data["data"][0]["user_login"]

    def get_streams_id(self, channel_name):
        url = "https://api.twitch.tv/helix/streams"
        params = {"user_login": channel_name, "type": "live"}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    async def chat(self):
        """Connect to Twitch chat via WebSocket and join specified channels."""
        async with websockets.connect(self.ws_url) as websocket:
            self.websocket = websocket
            await self.websocket.send(f"PASS oauth:{self.access_token}")
            await self.websocket.send("NICK justinfan123")  # Placeholder username

            # Listen to incoming messages
            await self.listen_to_chat()

    async def listen_to_chat(self):
        """Listen to chat messages and respond to PING to keep connection alive."""
        try:
            async for message in self.websocket:
                if "PRIVMSG" in message:
                    self.handle_message(message)
                elif message.startswith("PING"):
                    await self.websocket.send("PONG :tmi.twitch.tv")
        except websockets.ConnectionClosed:
            print("WebSocket connection closed.")
        except Exception as e:
            print(f"An error occurred: {e.with_traceback()}")

    def handle_message(self, message: websockets.Data):
        """Handle and process chat messages."""
        if isinstance(message, bytes):
            message = message.decode("utf-8")

        _, _, channel_message = message.partition("PRIVMSG")
        channel, _, message = channel_message.partition(":")
        channel = channel.strip()
        message = message.strip()
        msg_class = Message(message)
        channel = channel.removeprefix("#")
        streamer_id = self.name_to_id[channel]

        self.connected_chats[streamer_id].append(msg_class)

    async def join_room(self, stream_id: str):
        """Join a specific chat room dynamically."""
        if stream_id not in self.connected_chats:
            name = self.get_streamer_login(stream_id)
            await self.websocket.send(f"JOIN #{name}")

            self.name_to_id[name] = stream_id
            self.id_to_name[stream_id] = name
            self.connected_chats[stream_id] = deque(maxlen=100)
            print(f"Joined chat for #{name}")
        else:
            print(f"Already in chat with id: {stream_id}")

    async def leave_room(self, stream_id: str):
        """Leave a specific chat room dynamically."""
        if stream_id in self.connected_chats:
            name = self.id_to_name[stream_id]
            try:
                await self.websocket.send(f"PART #{name}")
            except websockets.ConnectionClosed:
                print("WebSocket connection closed.")

            del self.connected_chats[stream_id]
            del self.name_to_id[name]
            del self.id_to_name[stream_id]

            print(f"Left chat for #{name}")
        else:
            print(f"Not currently in chat for id: {stream_id}")

    async def close(self):
        """Close the Twitch chat connection and cancel the background task."""
        if self.chat_task:
            self.chat_task.cancel()  # Cancel the background task
            print("Chat task cancelled.")

        if self.websocket and self.websocket.open:
            await self.websocket.close()
            print("WebSocket connection closed.")

        self.chat_task = None
        self.websocket = None
        print("TwitchAPI has been shut down.")


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
twitch = TwitchAPI(CLIENT_ID, CLIENT_SECRET)


if __name__ == "__main__":
    pass
    # twitch_api = TwitchAPI(CLIENT_ID, CLIENT_SECRET)
    # twitch_api.auth(CLIENT_ID, CLIENT_SECRET)
    # # print(json.dumps(twitch_api.get_user_info("filian"), indent=4))
    # print(json.dumps(twitch_api.get_streams("198633200"), indent=4))
    # twitch_api.make_user_auth()
    # code = "code"
    # twitch_api.auth_user(code)
    # twitch_api.ref_token("ref_token")
