"""
File used for checking health of services
"""
import logging
from typing import Dict

from fastapi import HTTPException
from app.config_manager import Status, Service

from app.request import perform_async_request, AsyncResponse

logger = logging.getLogger(__name__)


class HealthStatusManager:
    """
    A HealthStatus manager stores
    the health status of services in memory
    to reduce strain on service endpoints and increase
    api response time
    """
    def __init__(self):
        self._statuses: Dict[str, Status] = {}

    def initialize_statuses(self, services):
        """
        Set all initial services to unknown
        to avoid 404 for existing services
        """
        for service in services:
            self._statuses[service.id] = Status.UNKNOWN

    def update_status(self, service_id: str, status: Status):
        self._statuses[service_id] = status

    def get_status(self, service_id: str) -> Status:
        try:
            return self._statuses[service_id]
        except KeyError:
            raise HTTPException(status_code=404, detail="Status not found for the specified service ID")


async def perform_health_check(
        service: Service,
        manager: HealthStatusManager,
        response_time_threshold=5,
        timeout_threshold=30):
    """
    Perform a health check for a given service
    :param service: The service to check
    :param manager: An instance of HealthStatusManager to store the health status in
    :param response_time_threshold: Maximum amount of time to be considered a healthy service
    :param timeout_threshold: Any service taking longer than this will be considered DOWN, a service inbetween the
    threshold and the timeout will be considered DODGY
    :return: None, it just updates the health status manager
    """
    logger.info(f"Starting health check for service {service.id}")

    # Fetch a response from the endpoint
    response: AsyncResponse = await perform_async_request(service.health_check_url, timeout_threshold)

    # If error is not None, we assume the service is DOWN
    if response.error:
        manager.update_status(service.id, Status.DOWN)
    else:
        if response.status_code == 200:

            # If we receive a 200 but it took longer than the response_time_threshold it's marked as DODGY
            if response.elapsed_time > response_time_threshold:
                manager.update_status(service.id, Status.DODGY)

            # A normal healthy service
            else:
                manager.update_status(service.id, Status.UP)

        # The service is in maintenance mode
        elif response.status_code == 503:
            manager.update_status(service.id, Status.MAINTENANCE)

        # Any other status code is considered DOWN
        else:
            manager.update_status(service.id, Status.DOWN)