from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# from twitch_api import twitch_client
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan():
    # INIT TWITCH CLIENT
    # INIT SOCKET MANAGER
    yield

    # CLOSE TWITCH CLIENT
    # CLOSE SOCKET MANAGER


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
