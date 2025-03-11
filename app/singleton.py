import threading


class SingletonMeta(type):
    """Thread-safe Singleton Metaclass"""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:  # Ensures thread safety
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """Thread-safe Singleton Base Class"""
    pass
