"""
Functions and classes for making requests
"""
from aiohttp import ClientSession, ClientTimeout, ClientError
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class AsyncResponse:
    """
    A dataclass to represent a response from an asynchronous request
    """
    status_code: int = None
    elapsed_time: float = None
    error: str = None
    body: dict = None


async def perform_async_request(
        url: str,
        timeout_threshold: int) -> AsyncResponse:
    """
    Perform an asynchronous HTTP GET request. This is so a slow
    connection to a service does not slow down the whole application
    :param url: URL to make the request to.
    :param timeout_threshold: Maximum time in seconds for the request before considering it timed out.
    :return: AsyncResponse object containing response data
    """
    async with ClientSession() as session:
        try:

            # Setup of a timeout with the specified parameter
            timeout = ClientTimeout(total=timeout_threshold)

            # Start a timer to see how long the request takes
            start_time = asyncio.get_event_loop().time()

            # Perform a GET request on the url
            async with session.get(url, timeout=timeout) as response:
                elapsed = asyncio.get_event_loop().time() - start_time

                # Get the content of the response
                body = await response.json()

                # Return a AsyncResponse object with the details of the response
                return AsyncResponse(status_code=response.status, elapsed_time=elapsed, body=body)
        # The request took too long
        except asyncio.TimeoutError:
            logger.error(f"Timeout while trying to reach {url}")
            return AsyncResponse(error='timeout')
        # General client error exception
        except ClientError as e:
            logger.error(f"Error during request to {url}: {str(e)}")
            return AsyncResponse(error='client_error')
