import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Depends
from starlette.responses import FileResponse, JSONResponse

from app.config_manager import ConfigManager, Service, Status
from app.dependencies import get_config_manager, get_scheduler, get_status_manager
from app.health_check import perform_health_check, HealthStatusManager
from app.load_image import load_image
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.version_check import perform_version_check

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Defines the lifespan of a FastAPI application,
    first we start the schedules and initializes our status managers,
    we then accept requests using YIELD and after this we can shut down the
    schedule.
    :param _app: The instance of the FastAPI application.
    """

    # Dependency
    config_manager = get_config_manager()
    scheduler = get_scheduler()
    status_manager = get_status_manager()

    # Initialize the status of all services on startup, to avoid 404's as soon as the app starts up
    status_manager.initialise_statuses(config_manager.services.values())

    # Run the initial health checks asynchronously
    await perform_periodic_health_checks()

    # Setup Cron pings for each service
    for service in config_manager.services.values():

        # Extract the ping cron for this given service
        ping_cron = service.ping_cron
        logger.info(f"Scheduling health check for {service.name} with cron '{ping_cron}'")

        # Add this cron to the schedule
        scheduler.add_job(perform_health_check, CronTrigger.from_crontab(ping_cron), args=[service, status_manager])

    scheduler.start()

    # Run the app
    yield

    # On shutdown, stop the scheduler
    scheduler.shutdown()


app = FastAPI(title="LISA", lifespan=lifespan)


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

