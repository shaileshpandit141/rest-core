from typing import Any

from rest_framework.renderers import JSONRenderer

from ..throttle_inspector import ThrottleInspector


class StructuredJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that standardizes API responses across the application.

    Adds metadata and consistent formatting for both success and error responses.

    Standard Response Format:
    ```
    {
        "status": "succeeded" | "failed",
        "status_code": int,
        "message": str,
        "data": Any | null,
        "errors": Any | null,
        "meta": {
            "rate_limits": {
                "throttled_by": str | null,
                "throttles": {
                    "name": {
                        "limit": int,
                        "remaining": int,
                        "reset_time": str,
                        "retry_after": str
                    }
                }
            }
        }
    }
    ```

    Notes:
        - For 2xx responses, `data` is populated and `errors` is null.
        - For error responses (non-2xx), `errors` is populated and `data` is null.
        - For 204 No Content, the response is untouched.
        - Throttle rate-limiting info is added to `meta.rate_limits` if available.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None) -> bytes:
        # If renderer context is missing, fallback to default rendering
        if renderer_context is None:
            return super().render(data, accepted_media_type, renderer_context)

        response = renderer_context.get("response")
        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code
        throttle_info: dict[str, Any] = {}

        # Attempt to get view context for throttle introspection
        view = renderer_context.get("view")
        if view is not None:
            inspector = ThrottleInspector(view)
            throttle_info = inspector.get_details()
            inspector.attach_headers(response, throttle_info)

        # Construct initial payload
        payload: dict[str, Any] = {
            "status": "succeeded",
            "status_code": status_code,
            "message": getattr(response, "status_text", ""),
            "data": data,
            "errors": None,
            "meta": {
                "rate_limits": throttle_info,
            },
        }

        # Update response message if available
        if hasattr(response, "message"):
            payload["message"] = response.message

        # If status is not 2xx, consider it a failed response
        if not str(status_code).startswith("2") and status_code != 204:
            payload["status"] = "failed"
            payload["errors"] = payload["data"]
            payload["data"] = None

        # If status code is 204 No Content, return empty response
        if status_code == 204:
            # Check if the renderer is accepted
            accepted_renderer = getattr(response, "accepted_renderer", None)

            # Check if the accepted renderer is the StructuredJSONRenderer
            if accepted_renderer is self:
                # Set the headers to indicate no content
                setattr(
                    response,
                    "headers",
                    {
                        **response.headers,
                        "Content-Length": "0",
                    },
                )

                # Return empty response
                return super().render(
                    None,
                    accepted_media_type=accepted_media_type,
                    renderer_context=renderer_context,
                )
            else:
                # If the accepted renderer is not the StructuredJSONRenderer,
                # return the original response
                return super().render(
                    data,
                    accepted_media_type=accepted_media_type,
                    renderer_context=renderer_context,
                )

        # Retuen Final rendered payload
        return super().render(payload, accepted_media_type, renderer_context)
