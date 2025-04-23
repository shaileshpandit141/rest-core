import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ResponseTimeMiddleware:
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
