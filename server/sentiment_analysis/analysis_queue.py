import queue
import threading

from sentiment_analysis.main import SentimentAnalysis
from app import twitch, socket_manager


class AnalysisQueue:
    def __init__(self, task, model, device):
        self.sent_model = SentimentAnalysis(task, model, device)
        self.task_queue = queue.Queue()  # Thread-safe queue for stream IDs
        self._is_running = False  # Control flag for the worker thread
        self._worker_thread = None  # The worker thread

    def _worker(self):
        """Worker thread that processes streams one at a time."""
        while self._is_running:
            try:
                # Wait for the next stream ID from the queue
                stream_id = self.task_queue.get(timeout=1)
                try:
                    messages_test = list(twitch.connected_chats[stream_id])
                    results = (
                        self.sent_model.multiple_message_classification_harmonic_mean(
                            messages_test
                        )
                    )

                    print(f"Stream {stream_id} results: {results}")
                    socket_manager.send_message(results, stream_id)

                except Exception as e:
                    print(f"Error processing stream {stream_id}: {e}")
                finally:
                    # Mark the task as done
                    self.task_queue.task_done()
            except queue.Empty:
                # If the queue is empty, continue looping
                continue

    def start(self):
        """Start the worker thread."""
        if not self._is_running:
            self._is_running = True
            self._worker_thread = threading.Thread(target=self._worker)
            self._worker_thread.daemon = True  # Optional: make the thread a daemon
            self._worker_thread.start()
            print("Analysis started.")

    def close(self):
        """Stop the worker thread and wait for it to finish."""
        if self._is_running:
            self._is_running = False
            # Wait for all queued tasks to be processed
            self.task_queue.join()
            # Wait for the worker thread to finish
            self._worker_thread.join(timeout=1)
            print("Analysis stopped.")

    def add_stream(self, stream_id):
        """Add a new stream ID to the queue."""
        self.task_queue.put(stream_id)
        print(f"Added stream: {stream_id}")

    def remove_stream(self, stream_id):
        """Remove a specific stream ID from the queue if it hasn't been processed yet."""
        with self.task_queue.mutex:
            try:
                self.task_queue.remove(stream_id)
                print(f"Removed stream: {stream_id}")
            except ValueError:
                print(
                    f"Stream {stream_id} not found in the queue or already being processed."
                )
