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
