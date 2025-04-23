import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ResponseTimeMiddleware:
    """
    A Django middleware class that measures and logs response time for each request.
    This middleware adds response time information both to the response headers
    and server logs. It uses the high-resolution performance counter to measure
    the time taken to process each request.
    Attributes:
        get_response (callable): The next middleware or view in the Django stack.
    Example:
        To use this middleware, add it to your MIDDLEWARE setting in Django settings:
        MIDDLEWARE = [
            'rest_core.middlewares.ResponseTimeMiddleware',
            ...
        ]
    Note:
        The response time is measured in seconds and rounded to 6 decimal places.
        The timing includes the entire request-response cycle.
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request) -> Any:
        start_time = time.perf_counter()
        response = self.get_response(request)
        end_time = time.perf_counter()

        response_time = f"{round(end_time - start_time, 6)} seconds"
        response["X-Response-Time"] = response_time

        logger.info(f"Request processed in {response_time}")

        return response
