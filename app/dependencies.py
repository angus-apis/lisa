from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config_manager import ConfigManager
from app.health_check import HealthStatusManager


def get_status_manager():
    """
    Tiny helper function used to retrieve an instance
    of the health status manager. For use with FastAPI dependency injection
    """
    return HealthStatusManager()


def get_config_manager():
    """
    Tiny helper function used to retrieve an instance
    of the config manager. For use with FastAPI dependency injection
    """
    return ConfigManager("config/services.yaml")

