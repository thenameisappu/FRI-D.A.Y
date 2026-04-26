import threading
import logging

logger = logging.getLogger(__name__)

class TaskManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.voice_lock = threading.Lock()
        self.mic_lock = threading.Lock()
        self.tasks = []
        self._initialized = True
        logger.info("TaskManager initialized.")

    def run_in_background(self, target, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        self.tasks.append(thread)
        logger.info(f"Started background task: {target.__name__}")
        return thread

    def cleanup_finished_tasks(self):
        self.tasks = [t for t in self.tasks if t.is_alive()]
