from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse, FileResponse, Response

from app.config_manager import Status, Service, ConfigManager
from app.dependencies import get_status_manager, get_config_manager
from app.health_check import HealthStatusManager
from app.load_image import load_image
from app.version_check import perform_version_check

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


@router.get("/badge/status/{service_id}")
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


@router.get("/badge/version/{service_id}")
async def get_version_badge(
        service_id: str,
        config_manager: Annotated[ConfigManager, Depends(get_config_manager)]
) -> Response:
    """
    Generate an SVG badge with the version of the service
    :param service_id: The ID of the service to get the badge of
    :param config_manager: An instance of a config manager to fetch status' from
    """
    service: Service = config_manager.get_service_by_id(service_id)
    version: str = await perform_version_check(service)

    SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
        <rect rx="3" width="120" height="20" fill="#555"/>
        <rect rx="3" x="50" width="70" height="20" fill="#4c1"/>
        <text x="10" y="14" fill="#fff" font-family="Verdana" font-size="11">Version</text>
        <text x="60" y="14" fill="#fff" font-family="Verdana" font-size="11">{version}</text>
    </svg>"""
    svg_content = SVG_TEMPLATE.format(version=version)
    return Response(content=svg_content, media_type="image/svg+xml")


@router.get("/version/{service_id}")
async def get_service_version(
        service_id: str,
        config_manager: Annotated[ConfigManager, Depends(get_config_manager)]
) -> JSONResponse:
    """
    Get the current version of a service
    :param service_id: The ID of the service to get the version of
    :param config_manager: The config manager to fetch the service from
    """

    service: Service = config_manager.get_service_by_id(service_id)
    version: str = await perform_version_check(service)
    return JSONResponse({"version": version})




