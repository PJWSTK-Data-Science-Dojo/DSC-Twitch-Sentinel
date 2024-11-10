
from datetime import datetime


class Message:
    def __init__(self, content: str):
        content: str = content
        timestamp: datetime | None = datetime.now()
