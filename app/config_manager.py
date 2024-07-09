"""
Responsible for loading and managing configuration from the config directory
"""

from enum import Enum, auto

import yaml
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel


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
    ping_cron: str = "*/5 6-21 * * *" # Default to every 5 minutes between 6am and 9pm


class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.services = self.load_config()

    def load_config(self) -> Dict[str, Service]:
        """
        Load services in a dict, [service_id -> Service]
        :return:
        """
        with open(self.config_path, 'r') as file:
            config_data = yaml.safe_load(file)
            return {service['id']: Service(**service) for service in config_data['services']}

    def get_service_by_id(self, service_id: str) -> Service:
        service = self.services.get(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service
