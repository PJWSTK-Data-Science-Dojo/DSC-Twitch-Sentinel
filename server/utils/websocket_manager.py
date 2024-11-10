from fastapi_socketio import SocketManager
from socketio.exceptions import DisconnectedError

from .stream_context import StreamContext

from .client import Client
from twitch_api import twitch
from utils.config import LOGGER


class WebSocketManager:
    def __init__(self, sm_app: SocketManager):
        self.all_clients: dict[str, Client] = dict()
        self.stream_clients: dict[str, set[str]] = {}
        self.sm_app = sm_app

    def add_client(self, client: Client):
        if client.sid in self.all_clients:
            return

        self.all_clients[client.sid] = client

    async def update_client(self, sid: str, stream_context: StreamContext):
        if sid not in self.all_clients:
            raise Exception(f"Client with sid {sid} not found")

        client = self.all_clients[sid]
        client.stream_id = stream_context.channelId

        if stream_context.channelId not in self.stream_clients:
            self.stream_clients[stream_context.channelId] = set()

        self.stream_clients[stream_context.channelId].add(client.sid)

    async def remove_client(self, sid: str):
        if sid not in self.all_clients:
            raise Exception(f"Client with sid {sid} not found")

        client = self.all_clients[sid]

        if client.stream_id:
            self.stream_clients[client.stream_id].remove(client.sid)
            if not self.stream_clients[client.stream_id]:
                await self.delete_stream(client.stream_id)

        del self.all_clients[sid]

        await self.send_disconnect(sid)

    async def send_message(self, message: str, stream_id: str):
        if stream_id not in self.stream_clients:
            raise Exception(f"Stream with id {stream_id} not found")

        for client_sid in list(self.stream_clients[stream_id]):
            await self.sm_app.emit("data", message, to=client_sid)

    async def delete_stream(self, stream_id: str):
        if stream_id not in self.stream_clients:
            raise Exception(f"Stream with id {stream_id} not found")

        for client in list(self.stream_clients[stream_id]):
            await self.remove_client(client.sid)

        del self.stream_clients[stream_id]
        await twitch.leave_room(stream_id)
        # TODO JOB QUEUE

    async def close(self):
        for stream_id in self.stream_clients:
            for sid in self.stream_clients[stream_id]:
                await self.sm_app.emit("disconnect", to=sid)

        self.stream_clients.clear()

    async def send_disconnect(self, sid: str):
        try:
            await self.sm_app.emit("disconnect", to=sid)
        except DisconnectedError:
            LOGGER.error(f"Client {sid} already disconnected")
