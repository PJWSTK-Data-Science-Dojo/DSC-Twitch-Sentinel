from datetime import datetime


class Message:
    def __init__(self, content: str):
        self.content: str = content
        self.timestamp: datetime | None = datetime.now()
