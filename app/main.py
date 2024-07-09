import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from pydantic import Json
from starlette.responses import FileResponse, JSONResponse

from app.config_manager import ConfigManager, Service, Status
from app.health_check import perform_health_check, HealthStatusManager
from app.load_image import load_image
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.version_check import perform_version_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the status of all services on startup
    status_manager.initialize_statuses(config_manager.services.values())

    # Run the initial health checks asynchronously
    await perform_periodic_health_checks()

    # Start the schedule
    scheduler.start()

    # Every five minutes ping all the apps
    scheduler.add_job(perform_periodic_health_checks, 'interval', minutes=5)

    # Run the app
    yield

    # On shutdown, stop the scheduler
    scheduler.shutdown()


app = FastAPI(title="LISA", lifespan=lifespan)
config_manager = ConfigManager("config/services.yaml")
scheduler = AsyncIOScheduler()
status_manager = HealthStatusManager()


def get_status_manager():
    """
    Tiny helper function used to retrieve an instance
    of the health status manager. For use with FastAPI dependency injection
    """
    return status_manager


@app.get("/health/{service_id}")
async def get_service_health(
        service_id: str,
        manager: Annotated[HealthStatusManager, Depends(get_status_manager)]
):
    """
    Fetch the health status of a service
    :param service_id: The ID of the service
    :param manager: An instance of a health status manager to fetch status' from
    """
    status: Status = await manager.get_status(service_id)
    return JSONResponse({"service_id": service_id, "status": status.name})


@app.get("/badge/{service_id}")
async def get_service_badge(
        service_id: str,
        manager: Annotated[HealthStatusManager, Depends(get_status_manager)]
) -> FileResponse:
    """
    Generate an SVG badge which indicates the status
    of this service
    :param service_id: The ID of the service to get the badge of
    :param manager: An instance of a health status manager to fetch status' from
    """
    return await load_image(manager.get_status(service_id))


@app.get("/version/{service_id}")
async def get_service_version(
        service_id: str,
) -> Json:
    """
    Get the current version of a service
    :param service_id: The ID of the service to get the version of
    """

    service: Service = config_manager.get_service_by_id(service_id)
    version: str = await perform_version_check(service)
    return JSONResponse({"version": version})


@app.get("/")
async def root():
    return {"message": "Welcome to LISA"}


# -------------- Schedules -----------------

async def perform_periodic_health_checks():
    """
    Periodically check all the services, instead of doing it ONLY when we get an API request.
    """

    # Check the health of all services asynchronously to avoid waiting for unresponsive apps
    tasks = []
    for service in config_manager.services.values():
        task = asyncio.create_task(perform_health_check(service, status_manager))
        tasks.append(task)
    await asyncio.gather(*tasks)

