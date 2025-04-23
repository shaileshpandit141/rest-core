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
