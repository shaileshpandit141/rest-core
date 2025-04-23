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
