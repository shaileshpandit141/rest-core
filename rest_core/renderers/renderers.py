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
