import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager

# from twitch_api import twitch_client
from contextlib import asynccontextmanager
from utils.websocket_manager import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sm_app
    # INIT TWITCH CLIENT
    # INIT SOCKET MANAGER
    # INIT JOB QUEUE

    yield

    # CLOSE JOB QUEUE
    # CLOSE TWITCH CLIENT
    # CLOSE SOCKET MANAGER


app = FastAPI(lifespan=lifespan)
origins = [
    "https://localhost:3000",  # Example for local development (adjust as needed)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Set origins that are allowed to communicate with this API
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

sm_app = SocketManager(app=app)


@sm_app.on("connect")
async def handle_connect():
    print(f"Client connected")


@sm_app.on("disconnect")
async def handle_disconnect():
    print(f"Client disconnected")


@sm_app.on("message")
async def handle_message(sid, data):
    print(f"Received message from {sid}: {data}")
    await sm_app.emit("response", f"Echo: {data}", to=sid)


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
