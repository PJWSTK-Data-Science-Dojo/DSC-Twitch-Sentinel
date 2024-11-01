from pydantic import BaseModel


class Client(BaseModel):
    sid: str
    stream_id: str | None = None
