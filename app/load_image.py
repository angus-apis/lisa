"""
Serve images from file
"""

import os

from starlette.responses import FileResponse

from app import PROJECT_DIR
from app.config_manager import Status

# Get the image directory
IMAGE_DIR = os.path.join(PROJECT_DIR, 'images')

# Map status to image filename
status_to_image = {
    Status.UP: "normal.svg",
    Status.DOWN: "error.svg",
    Status.DODGY: "dodgy.svg",
    Status.UNKNOWN: "mystery.svg"
}


async def load_image(status: Status) -> FileResponse:
    """
    Given a service status, load
    an appropriate SVG
    """

    # Determine the appropriate image file based on the status
    image_file = status_to_image.get(status, "mystery.svg")
    image_path = os.path.join(IMAGE_DIR, image_file)

    return FileResponse(image_path, media_type='image/svg+xml')
