from typing import Any, Optional, Union

from rest_framework.response import Response as DrfResponse


class Response(DrfResponse):
    """
    A custom Response class that extends Django Rest Framework's Response.

    This class provides a standardized way to format API responses by wrapping the data
    in a consistent structure with a message and data.

    Args:
        message (Optional[str]): A message to include in the response. Defaults to None.
        data (Optional[Union[dict[str, Any], list[Any]]]): The data data to be included
            in the response. Can be a dictionary or list. Defaults to None.
        status (Optional[int]): The HTTP status code for the response. Defaults to None.
        headers (Optional[dict[str, str]]): Additional headers to include in the response.
            Defaults to None.
        exception (bool): Whether the response is an exception response. Defaults to False.
        content_type (Optional[str]): The content type of the response. Defaults to None.

    Example:
        ```python
        response = Response(
            message="Success",
            data={"user": "john_doe"},
            status=200
        ```

    Returns:
        Response object with formatted data in the structure:
        {
            "message": str,
            "data": Union[dict, list]
        }
    """

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
            "data": data,
        }

        super().__init__(
            data=formatted_data,
            status=status,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )
