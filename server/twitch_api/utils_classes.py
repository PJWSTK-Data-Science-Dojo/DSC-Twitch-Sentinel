from datetime import datetime


class Message:
    def __init__(self, content: str):
        self.content: str = content
        self.timestamp: datetime | None = datetime.now()

    def __str__(self):
        return self.content

    def __repr__(self) -> str:
        return f"Message(content={self.content}, timestamp={self.timestamp})"
