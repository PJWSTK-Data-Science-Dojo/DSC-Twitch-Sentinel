import socketio
import sentiment_analysis.analysis_queue as aq
from utils.websocket_manager import WebSocketManager
from utils.stream_context import StreamContext
from .client import Client
from twitch_api import twitch

sio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
sio_app = socketio.ASGIApp(socketio_server=sio_server, socketio_path="sockets")

socket_manager = WebSocketManager(sio_server)


@sio_server.event
async def connect(sid, environ, *args):
    print(f"Client {sid} connected")

    client = Client(sid=sid)
    socket_manager.add_client(client=client)


@sio_server.event
async def disconnect(sid):
    await socket_manager.remove_client(sid)
    print(f"Client {sid} disconnected")


@sio_server.event
async def message(sid, data):
    await sio_server.emit("response", f"Echo: {data}", to=sid)


@sio_server.on("stream_context")
async def stream_context(sid, data):
    try:
        # Validate the incoming data using StreamContext model
        context = StreamContext.model_validate(data)

        await sio_server.emit("response", f"Echo: {context}", to=sid)
        await socket_manager.update_client(sid, context)
        await twitch.join_room(context.channelId)
        await aq.analysis_queue.add_stream(context.channelId)

    except Exception as e:
        print(f"Error processing stream context: {e}")
        await sio_server.emit("error", "Invalid data format for stream context", to=sid)
