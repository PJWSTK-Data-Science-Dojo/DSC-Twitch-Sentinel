from collections import deque


class JobQueue:
    def __init__(self) -> None:
        self.queue: deque[str] = deque()

    def add(self, job: str) -> None:
        self.queue.append(job)
