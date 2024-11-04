import asyncio
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from twitch_api import twitch_client
from contextlib import asynccontextmanager
from utils.sockets import sio_app, socket_manager, sio_server
import logging
from twitch_api import twitch

logging.basicConfig(level=logging.ERROR)

sessions = []


async def test_thread():
    while True:
        for sid, client in socket_manager.all_clients.items():
            print(f"Sending chat to {sid}")
            await sio_server.emit(
                "chat",
                {
                    "chat_entertainment": random.random(),
                },
                to=sid,
            )
        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sio_app, socket_manager
    await twitch.start()

    # INIT JOB QUEUE
    yield
    # CLOSE JOB QUEUE
    await socket_manager.close()
    await twitch.close()


app = FastAPI(lifespan=lifespan)
app.mount(path="/sockets", app=sio_app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:3000"
    ],  # Set origins that are allowed to communicate with this API
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/streams/{stream_name}/info", status_code=200)
async def get_info_stream(stream_name: str):
    print("get info chat")
    return twitch.get_streams_name(stream_name)


@app.get("/streams", status_code=200)
async def get_streams():
    keys = twitch.connected_chats.keys()
    return list(keys)


@app.get("/streams/{stream_name}/listen", status_code=200)
async def listen_stream(stream_name: str):
    print("Listening to stream")

    await twitch.join_room(stream_name)
    return {"status": "ok"}


@app.get("/streams/{stream_name}/chat", status_code=200)
async def get_chat(stream_name: str):
    print("Getting chat")
    return twitch.connected_chats[stream_name]


@app.get("/streams/{stream_name}/leave")
async def leave_stream(stream_name: str):
    await twitch.leave_room(stream_name)
    return {"status": "ok"}
