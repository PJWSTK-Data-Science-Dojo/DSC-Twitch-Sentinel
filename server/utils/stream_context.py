from pydantic import BaseModel


class StreamContext(BaseModel):
    channelId: str
    clientId: str
    helixToken: str
    userId: str
