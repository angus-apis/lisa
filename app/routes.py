from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse, FileResponse

from app.config_manager import Status, Service
from app.health_check import HealthStatusManager
from app.load_image import load_image

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Welcome to LISA"}


@router.get("/health/{service_id}")
async def get_service_health(
        service_id: str,
        manager: Annotated[HealthStatusManager, Depends(get_status_manager)]
):
    """
    Fetch the health status of a service
    :param service_id: The ID of the service
    :param manager: An instance of a health status manager to fetch status' from
    """
    status: Status = manager.get_status(service_id)
    return JSONResponse({"service_id": service_id, "status": status.name})


@router.get("/badge/{service_id}")
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


@router.get("/version/{service_id}")
async def get_service_version(
        service_id: str,
) -> JSONResponse:
    """
    Get the current version of a service
    :param service_id: The ID of the service to get the version of
    """

    service: Service = config_manager.get_service_by_id(service_id)
    version: str = await perform_version_check(service)
    return JSONResponse({"version": version})




