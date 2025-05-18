from typing import TypedDict

from rest_framework.response import Response
from rest_framework.status import is_success


class ActionMessages(TypedDict, total=False):
    list: str
    retrieve: str
    create: str
    update: str
    partial_update: str
    destroy: str


class ErrorMessages(TypedDict, total=False):
    validation_error: str
    not_found: str


class MessagesDict(TypedDict):
    actions: ActionMessages
    errors: ErrorMessages


class ActionMessageMixin:
    """
    Sets response.message for view actions and known errors.
    Works across all class-based views (GenericAPIView, ViewSet, etc.)
    by inferring the action from HTTP method and context.
    """

    default_messages: MessagesDict = {
        "actions": {
            "list": "Data retrieved successfully.",
            "retrieve": "Resource fetched successfully.",
            "create": "Resource created successfully.",
            "update": "Resource updated successfully.",
            "partial_update": "Resource partially updated successfully.",
            "destroy": "Resource deleted successfully.",
        },
        "errors": {
            "validation_error": "Invalid input. Please review the provided data.",
            "not_found": "The requested resource could not be found.",
        },
    }

    messages: MessagesDict = {
        "actions": {},
        "errors": {},
    }

    @property
    def merged_messages(self) -> MessagesDict:
        return {
            "actions": {
                **self.default_messages["actions"],
                **(self.messages.get("actions") or {}),
            },
            "errors": {
                **self.default_messages["errors"],
                **(self.messages.get("errors") or {}),
            },
        }

    def get_action_type(self, request) -> str | None:
        """Determine the action based on HTTP method and view context."""
        method = request.method.lower()
        if method == "get":
            if hasattr(self, "get_object") and callable(
                getattr(self, "get_object", None)
            ):
                return "retrieve"
            return "list"
        elif method == "post":
            return "create"
        elif method == "put":
            return "update"
        elif method == "patch":
            return "partial_update"
        elif method == "delete":
            return "destroy"
        return None

    def finalize_response(self, request, response, *args, **kwargs) -> Response:
        response = super().finalize_response(request, response, *args, **kwargs)  # type: ignore

        # Determine action from attribute or fallback
        action = getattr(self, "action", None) or self.get_action_type(request)
        messages = self.merged_messages

        if response.status_code == 404 and getattr(response, "exception", False):
            msg = messages["errors"].get("not_found")
            if msg:
                response.message = msg
            return response

        if response.status_code == 400 and getattr(response, "exception", False):
            msg = messages["errors"].get("validation_error")
            if msg:
                response.message = msg
            return response

        if is_success(response.status_code) and action:
            msg = messages["actions"].get(action)
            if msg:
                response.message = msg

        return response
