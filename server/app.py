import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager

# from twitch_api import twitch_client
from contextlib import asynccontextmanager
from utils.client import Client
from utils.stream_context import StreamContext
from utils.websocket_manager import WebSocketManager
import logging

logging.basicConfig(level=logging.ERROR)

sessions = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sm_app, websocket_manager
    # INIT TWITCH CLIENT
    # INIT SOCKET MANAGER
    # INIT JOB QUEUE

    yield

    # CLOSE JOB QUEUE
    # CLOSE TWITCH CLIENT
    # CLOSE SOCKET MANAGER
    await websocket_manager.close()
    await sm_app._sio.shutdown()


app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "https://localhost:3000"
#     ],  # Set origins that are allowed to communicate with this API
#     allow_credentials=True,  # Allow cookies and other credentials
#     allow_methods=["*"],  # Allow all HTTP methods
#     allow_headers=["*"],  # Allow all headers
# )

sm_app = SocketManager(app=app, mount_location="/socket.io")
websocket_manager = WebSocketManager(sm_app)


@sm_app.on("connect")
async def handle_connect(sid, environ):
    print(f"Client {sid} connected")
    await sm_app.emit("connected", f"Hello from server!", to=sid)
    client = Client(sid=sid)
    websocket_manager.add_client(client)


@sm_app.on("disconnect")
async def handle_disconnect(sid):
    await websocket_manager.remove_client(sid)
    print(f"Client {sid} disconnected")


@sm_app.on("message")
async def handle_message(sid, data):
    await sm_app.emit("response", f"Echo: {data}", to=sid)


@sm_app.on("stream_context")
async def handle_message(sid, data: StreamContext):
    context = StreamContext.model_validate(data)
    print(f"Received stream context: {context}")

    await sm_app.emit("response", f"Echo: {context}", to=sid)

    websocket_manager.update_client(sid, context)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/streams")
async def get_streams():
    keys = websocket_manager.stream_clients.keys()
    return list(keys)


# @app.get("/streams/{stream_id}")
# async def get_stream(stream_id: str):
#     return websocket_manager.stream_clients.get(stream_id, [])
