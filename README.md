rest_core/
  - exceptions/
  - middlewares/
  - renderers/
  - response/
  - throttle_inspector/
  - __init__.py

<!-- exceptions/exceptions.py -->
from datetime import datetime
from typing import Any

import pytz
from django.core.cache import cache
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle


def base_exception_handler(exc, context) -> Any | Response | None:
    """A custom exception handler that returns the exception details in a custom format."""
    response = views.exception_handler(exc, context)
    request = context.get("request", None)

    # Apply throttling if any exception is raised
    if request is not None:
        # Get the view (if available)
        view = context.get("view", None)

        is_authenticated = request.user.is_authenticated
        if is_authenticated:
            # Use view-defined throttle classes or fallback to AnonRateThrottle
            throttle_classes = getattr(view, "throttle_classes", None) or [
                AnonRateThrottle
            ]
        else:
            throttle_classes = [AnonRateThrottle]
            setattr(view, "throttle_classes", throttle_classes)

        # Iterate over the list of throttles class
        for throttle_class in throttle_classes:
            throttle = throttle_class()  # Instantiate the throttle class
            cache_key = throttle.get_cache_key(request, view)

            if cache_key:
                history = cache.get(cache_key, [])
                now = datetime.now(pytz.UTC).timestamp()

                # Remove expired requests from history
                history = [
                    timestamp
                    for timestamp in history
                    if now - timestamp < throttle.duration
                ]

                # Check if throttle limit is exceeded or not
                if isinstance(throttle.num_requests, int):
                    if len(history) >= throttle.num_requests:
                        retry_after = throttle.duration
                        if history:
                            retry_after = int(throttle.duration - (now - history[0]))

                        return Response(
                            {
                                "message": "You have exceeded the rate limit. Please wait before making more requests.",
                                "data": {
                                    "detail": "You have exceeded the rate limit. Please wait before making more requests.",
                                    "retry_after": retry_after,
                                },
                            },
                            status=status.HTTP_429_TOO_MANY_REQUESTS,
                        )

                # Otherwise, add the current request to history and update cache
                history.append(now)
                cache.set(cache_key, history, throttle.duration)

    # Return un updaed response instance
    return response

<!-- middlewares/middlewares.py -->
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

<!-- renderers/renderers.py -->
from datetime import datetime
from typing import Any
from uuid import uuid4

from rest_framework.renderers import JSONRenderer

from ..throttle_inspector import ThrottleInspector


class JSONBaseRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None) -> bytes:
        # If renderer_context is None, return the data as is
        if renderer_context is None:
            return super().render(data, accepted_media_type, renderer_context)

        # Get the response object from the renderer context
        response = renderer_context.get("response", None)

        # If the response object is not None, get the status code and status text
        if response is not None:
            status_code = response.status_code
            throttle_details: dict[str, Any] = {}

            # Access the view instance from the renderer context
            view = renderer_context.get("view", None)

            if view is not None:
                # Initialize ThrottleInspector class
                throttle_inspector = ThrottleInspector(view)

                # Inspect the throttles details
                throttle_details = throttle_inspector.get_details()

                # Attach throttle details in headers
                throttle_inspector.attach_headers(response, throttle_details)

            # Praper Initial payload data for response
            payload: dict[str, Any] = {
                "status": "succeeded",
                "status_code": status_code,
                "message": response.status_text,
                "data": None,
                "errors": None,
                "meta": {
                    "response_time": (
                        response.headers.get("X-Response-Time", "N/A")
                        if hasattr(response, "headers")
                        else "N/A"
                    ),
                    "request_id": str(uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "documentation_url": "N/A",
                    "rate_limits": throttle_details,
                },
            }

            # Handle Drf uper flexible response data
            if "message" in data:
                message = data["message"]
                if message is not None:
                    payload.update({"message": message})
            if "payload" in data:
                payload.update({"data": data["payload"]})
            else:
                payload.update({"data": data})

            # Detect Drf errors
            if not str(status_code).startswith("2"):
                payload.update(
                    {"status": "failed", "errors": payload["data"], "data": None}
                )
                return super().render(
                    payload,
                    accepted_media_type,
                    renderer_context,
                )

            # Handle success response
            if status_code == 204:
                return super().render(
                    None,
                    accepted_media_type,
                    renderer_context,
                )
            else:
                return super().render(
                    payload,
                    accepted_media_type,
                    renderer_context,
                )

        # If the response object is None, return the data as is
        return super().render(data, accepted_media_type, renderer_context)

<!-- response/response.py -->
from typing import Any, Optional, Union

from rest_framework.response import Response as DrfResponse


class Response(DrfResponse):
    def __init__(
        self,
        message: Optional[str] = None,
        data: Optional[Union[dict[str, Any], list[Any]]] = None,
        status: Optional[int] = None,
        headers: Optional[dict[str, str]] = None,
        exception: bool = False,
        content_type: Optional[str] = None,
    ) -> None:
        formatted_data: dict[str, Any] = {
            "message": message,
            "payload": data,
        }

        super().__init__(
            data=formatted_data,
            status=status,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )

<!-- throttle_inspector/throttle_inspector.py -->
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Type

import pytz
from django.conf import settings
from rest_framework.throttling import BaseThrottle

# Configure logging
logger = logging.getLogger(__name__)


class ThrottleInspector:
    """
    A class that inspects and retrieves details for DRF throttling,
    following Django REST Framework's default behavior.
    """

    def __init__(self, view_instance: Any) -> None:
        """
        Initializes the ThrottleInspector with the view instance.

        Args:
            view_instance (Any): The Django APIView instance.
        """
        self.view_instance = view_instance
        self.request = getattr(view_instance, "request", None)
        self.throttle_classes = getattr(view_instance, "throttle_classes", [])

        if not self.throttle_classes:
            logger.info(
                f"No throttles configured for {type(view_instance).__name__}. Returning empty response."
            )
        if not self.request:
            logger.warning(
                f"Request object is missing in {type(view_instance).__name__}."
            )

    @staticmethod
    def to_snake_case(name: str) -> str:
        """Converts UpperCamelCase to snake_case and removes 'RateThrottle' suffix."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name.replace("RateThrottle", "")).lower()

    @staticmethod
    def parse_rate(rate: str) -> Optional[Tuple[int, int]]:
        """Parses a rate string (e.g., '100/day') into (limit, duration_in_seconds)."""
        if not rate:
            return None
        match = re.match(r"(\d+)/(second|minute|hour|day)", rate)
        if not match:
            return None

        num_requests, period = match.groups()
        duration_map = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
        return int(num_requests), duration_map[period]

    def get_throttle_rate(
        self, throttle_class: Type[BaseThrottle]
    ) -> Optional[Tuple[int, int]]:
        """Retrieves and parses the throttle rate from Django settings."""
        throttle_name = self.to_snake_case(throttle_class.__name__)
        rate = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {}).get(
            throttle_name
        )

        if not rate:
            logger.warning(f"No rate limit found for {throttle_name}. Skipping.")

        return self.parse_rate(rate)

    def get_throttle_usage(
        self, throttle: BaseThrottle, limit: int, duration: int
    ) -> Dict[str, Any]:
        """Gets current request usage for a given throttle instance."""
        cache_key = throttle.get_cache_key(self.request, self.view_instance)  # type: ignore
        history = throttle.cache.get(cache_key, []) if cache_key else []  # type: ignore

        remaining = max(0, limit - len(history))
        first_request_time = (
            datetime.fromtimestamp(history[0], tz=pytz.UTC)
            if history
            else datetime.now(pytz.UTC)
        )
        reset_time = first_request_time + timedelta(seconds=duration)
        retry_after = max(0, int((reset_time - datetime.now(pytz.UTC)).total_seconds()))

        return {
            "limit": limit,
            "remaining": remaining,
            "reset_time": reset_time.isoformat(),
            "retry_after": f"{retry_after} seconds",
        }

    def get_details(self) -> Dict[str, Any]:
        """
        Retrieves throttle details for all specified throttle classes,
        following Django's default prioritization.
        If no throttles are configured, returns an empty dictionary `{}`.
        """
        if not self.throttle_classes:
            return {}  # Return empty dictionary if no throttles are set

        details: dict[str, Any] = {"throttled_by": None, "throttles": {}}

        for throttle_class in self.throttle_classes:
            throttle = throttle_class()
            parsed_rate = self.get_throttle_rate(throttle_class)

            if not parsed_rate:
                continue  # Skip if rate is not configured

            limit, duration = parsed_rate
            throttle_name = self.to_snake_case(throttle_class.__name__)
            throttle_usage = self.get_throttle_usage(throttle, limit, duration)

            details["throttles"][throttle_name] = throttle_usage

            if throttle_usage["remaining"] == 0 and not details["throttled_by"]:
                details["throttled_by"] = throttle_name
                logger.info(f"Request throttled by {throttle_name}")

        return details

    def attach_headers(self, response, throttle_details: Dict[str, Any] | None) -> None:
        """Attaches throttle details to the response headers."""
        if throttle_details is None:
            return None

        for throttle_type, data in throttle_details.get("throttles", {}).items():
            response[f"X-Throttle-{throttle_type}-Limit"] = str(data["limit"])
            response[f"X-Throttle-{throttle_type}-Remaining"] = str(data["remaining"])
            response[f"X-Throttle-{throttle_type}-Reset"] = data["reset_time"]
            response[f"X-Throttle-{throttle_type}-Retry-After"] = data["retry_after"]

        logger.info("Throttle headers attached to response.")
