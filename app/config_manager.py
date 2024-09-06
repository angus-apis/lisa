"""
Responsible for loading and managing configuration from the config directory
"""
import os
from enum import Enum, auto

import yaml
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv


class Status(Enum):
    UP = auto()           # App is up and running normally
    DOWN = auto()         # App is not responding to health check
    DODGY = auto()        # App took a long time to respond
    UNKNOWN = auto()      # Status is unknown (not yet checked status)
    MAINTENANCE = auto()  # App is down for planned maintenance
    FAILED = auto()       # An error occurred checking the health


class Service(BaseModel):
    id: str
    name: str
    description: str
    health_check_url: str
    version_url: str
    ping_cron: str = "*/5 6-21 * * *"  # Default to every 5 minutes between 6am and 9pm


class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.services = self.load_config()
        self.global_config = _load_global_config()

    def load_config(self) -> Dict[str, Service]:
        """
        Load services in a dict, [service_id -> Service]
        :return:
        """
        with open(self.config_path, 'r') as file:
            config_data = yaml.safe_load(file)
            return {service['id']: Service(**service) for service in config_data['services']}

    def _get_global_config_item(self, key: str) -> str:
        """
        Get a single config item from the .env file
        :param key: the config item to get e.g. APP_ENABLED
        :return: str: The value for the given key
        """
        return self.global_config.get(key, None)

    def get_service_by_id(self, service_id: str) -> Service:
        service = self.services.get(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service

    def is_ping_enabled(self) -> bool:
        """
        Are cron pings currently enabled or not?
        :return: Bool
        """
        return self._get_global_config_item("PING_ENABLED").lower() == "true"


def _load_global_config() -> Dict[str, str]:
    """
    Load config from the .env file

    APP_ENABLED: Should the service be enabled or disabled?
    PING_ENABLED: Should any of the service pings be running?
    """
    load_dotenv()
    return {
        "APP_ENABLED": os.getenv("APP_ENABLED", "true").lower(),
        "PING_ENABLED": os.getenv("PING_ENABLED", "true").lower()
    }
