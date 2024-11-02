import asyncio
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from twitch_api import twitch_client
from contextlib import asynccontextmanager
from utils.sockets import sio_app, socket_manager, sio_server
import logging

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
    test_thread_task = asyncio.create_task(test_thread())
    # INIT TWITCH CLIENT
    # INIT SOCKET MANAGER
    # INIT JOB QUEUE

    yield

    # CLOSE JOB QUEUE
    # CLOSE TWITCH CLIENT
    # CLOSE SOCKET MANAGER
    test_thread_task.cancel()
    try:
        await test_thread_task
    except asyncio.CancelledError:
        pass
    await socket_manager.close()


app = FastAPI(lifespan=lifespan)
app.mount(path="/", app=sio_app)

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


@app.get("/streams")
async def get_streams():
    keys = socket_manager.stream_clients.keys()
    return list(keys)


# @app.get("/streams/{stream_id}")
# async def get_stream(stream_id: str):
#     return websocket_manager.stream_clients.get(stream_id, [])
