import asyncio
import queue
import threading
import time


from .main import task, model, device, SentimentAnalysis
from twitch_api import twitch
import utils.sockets as usock


class AnalysisQueue:
    def __init__(self, task, model, device):
        self.sent_model = SentimentAnalysis(task, model, device)
        self.task_queue = queue.Queue()  # Thread-safe queue for stream IDs
        self._is_running = False  # Control flag for the worker thread
        self._worker_task = None  # The worker thread

    async def _worker(self):
        """Worker thread that processes streams one at a time."""
        while self._is_running:
            for stream_id in list(twitch.connected_chats.keys()):
                try:
                    messages_test = list(twitch.connected_chats[stream_id])
                    results = await asyncio.to_thread(
                        self.sent_model.multiple_message_classification_harmonic_mean,
                        messages_test,
                    )

                    await usock.socket_manager.send_message(results, stream_id)
                except Exception as e:
                    print(f"Error processing stream {stream_id}: {e}")
                await asyncio.sleep(0)  # Yield control to the event loop
            await asyncio.sleep(0.5)  # Delay between cycles

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._worker())
        except Exception as e:
            print("An error occurred in the bot thread: %s", e)

    async def start(self):
        """Start the worker thread."""
        self._is_running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        print("Analysis started.")

    async def close(self):
        """Stop the worker thread and wait for it to finish."""
        if self._is_running:
            self._is_running = False
            # Wait for all queued tasks to be processed
            self.task_queue.join()
            # Wait for the worker thread to finish
            self.thread.join()

            print("Analysis stopped.")

    async def add_stream(self, stream_id):
        """Add a new stream ID to the queue."""
        if stream_id in self.task_queue.queue:
            print(f"Stream {stream_id} already in the queue.")
            return

        self.task_queue.put(stream_id)
        print(f"Added stream: {stream_id}")

    def remove_stream(self, stream_id):
        """Remove a specific stream ID from the queue if it hasn't been processed yet."""
        with self.task_queue.mutex:
            try:
                self.task_queue.queue.remove(stream_id)
                print(f"Removed stream: {stream_id}")
            except ValueError:
                print(
                    f"Stream {stream_id} not found in the queue or already being processed."
                )


analysis_queue = AnalysisQueue(task, model, device)
