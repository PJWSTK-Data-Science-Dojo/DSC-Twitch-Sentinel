from fastapi import WebSocket


class WebSocketManager:

    def __init__(self):
        self.stream_clients: dict[str, list[WebSocket]] = {}

    async def add_client(self, client: WebSocket, stream_id: str):
        await client.accept()

        if stream_id not in self.stream_clients:
            self.stream_clients[stream_id] = []

        self.stream_clients[stream_id].append(client)

    def remove_client(self, client: WebSocket, stream_id: str):
        self.stream_clients[stream_id].remove(client)

        if not self.stream_clients[stream_id]:
            self.delete_stream(stream_id)

    async def send_message(self, message: str, stream_id: str):
        for client in self.stream_clients[stream_id]:
            try:
                await client.send_text(message)
            except Exception as e:
                print(f"Failed to send message to {client}: {e}")
                await self.remove_client(client, stream_id)

    def delete_stream(self, stream_id: str):
        if stream_id in self.stream_clients:
            del self.stream_clients[stream_id]


websocket_manager = WebSocketManager()
