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
    Sets response.message for view actions and known errors
    (auto-merging custom and default messages).
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

    def finalize_response(self, request, response, *args, **kwargs) -> Response:
        response = super().finalize_response(request, response, *args, **kwargs)  # type: ignore
        action = getattr(self, "action", None)

        # Only apply if inside a known action
        if not action:
            return response

        # Get Merge messages With default messages
        messages = self.merged_messages

        # 404 Not Found
        if response.status_code == 404 and getattr(response, "exception", False):
            msg = messages["errors"].get("not_found")
            if msg:
                response.message = msg
            return response

        # 400 Validation Error
        if response.status_code == 400 and getattr(response, "exception", False):
            msg = messages["errors"].get("validation_error")
            if msg:
                response.message = msg
            return response

        # Success response (200/201/etc)
        if is_success(response.status_code):
            msg = messages["actions"].get(action)
            if msg:
                response.message = msg

        return response
