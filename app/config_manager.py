import yaml
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel


class Service(BaseModel):
    id: str
    name: str
    description: str
    repo_url: str
    health_check_url: str


class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.services = self.load_config()

    def load_config(self) -> Dict[str, Service]:
        with open(self.config_path, 'r') as file:
            config_data = yaml.safe_load(file)
            return {service['id']: Service(**service) for service in config_data['services']}

    def get_service_by_id(self, service_id: str) -> Service:
        service = self.services.get(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service