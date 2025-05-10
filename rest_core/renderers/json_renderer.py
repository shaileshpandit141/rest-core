from datetime import datetime
from typing import Any
from uuid import uuid4

from rest_framework.renderers import JSONRenderer as DrfJSONRenderer

from ..throttle_inspector import ThrottleInspector


class JSONRenderer(DrfJSONRenderer):
    """A custom JSON renderer that extends Django REST Framework's JSONRenderer.

    This renderer provides a standardized JSON response format with additional metadata
    and error handling capabilities. It wraps the response data in a consistent structure
    that includes status, status code, message, data, errors, and metadata.

    Attributes:
        None

    Methods:
        render(data, accepted_media_type=None, renderer_context=None) -> bytes:
            Renders the response data into a standardized JSON format.

    Response Format:
        {
            "status": str,                  # "succeeded" or "failed"
            "status_code": int,             # HTTP status code
            "message": str,                 # Response message or status text
            "data": Any,                    # Response payload for successful requests
            "errors": Any,                  # Error details for failed requests
                "response_time": str,       # Response processing time
                "request_id": str,          # Unique request identifier
                "timestamp": str,           # UTC timestamp in ISO format
                "documentation_url": str,   # API documentation URL
                "rate_limits": dict         # Rate limiting information

    Notes:
        - For successful responses (2xx), data contains the response payload
        - For error responses, errors contains the error details and data is None
        - 204 No Content responses return None
        - Throttling information is automatically included in meta.rate_limits
        - Supports DRF's flexible response format with 'message' and 'payload' keys
    """

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
                    "response_time": "none",
                    "request_id": str(uuid4()),
                    "timestamp": datetime.utcnow().isoformat(),
                    "documentation_url": "none",
                    "rate_limits": throttle_details,
                },
            }

            # Handle Drf uper flexible response data
            if "message" in data:
                message = data["message"]
                if message is not None:
                    payload.update({"message": message})
            if "data" in data:
                payload.update({"data": data["data"]})
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
