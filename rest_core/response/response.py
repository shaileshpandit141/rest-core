from typing import Any, Optional

from rest_framework.response import Response as DrfResponse

from .types import APIResponseData, APIValidationErrors


class Response(DrfResponse):
    """
    A custom Response class that extends Django Rest Framework's Response.

    This class provides a standardized way to format API responses by wrapping the data
    in a consistent structure with a message and data.

    Args:
        message (Optional[str]): A message to include in the response. Defaults to None.
        data (Optional[Union[dict[str, Any], list[Any]]]): The data data to be included
            in the response. Can be a dictionary or list. Defaults to None.1

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
            "data": {"user": "john_doe"}
        }
    """

    def __init__(
        self,
        message: Optional[str] = None,
        data: Optional[APIResponseData | APIValidationErrors] = None,
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


def success_response(
    message: str,
    data: APIResponseData,
    status: int = 200,
    headers: Optional[dict[str, str]] = None,
    exception: bool = False,
    content_type: Optional[str] = None,
) -> Response:
    """
    Generate a standardized success response for API endpoints.

    Args:
        message (str): A message describing the success of the operation.
        data (APIResponseData): The data to include in the response body.
        status (int, optional): The HTTP status code for the response. Defaults to 200.
        headers (Optional[dict[str, str]], optional): Additional headers to include in the response. Defaults to None.
        exception (bool, optional): Whether the response is an exception response. Defaults to False.
        content_type (Optional[str], optional): The content type of the response. Defaults to None.

    Example:
        ```python
        response = success_response(
            message="Operation completed successfully.",
            data={"id": 123, "name": "John Doe"},
            status=200
        )
        ```

    Returns:
        Response object with formatted data in the structure:
        {
            "message": str,
            "data": {"id": 123, "name": "John Doe"}
        }
    """
    return Response(
        message=message,
        data=data,
        status=status,
        headers=headers,
        exception=exception,
        content_type=content_type,
    )


def failure_response(
    message: str,
    errors: APIValidationErrors,
    status: int = 404,
    headers: Optional[dict[str, str]] = None,
    exception: bool = False,
    content_type: Optional[str] = None,
) -> Response:
    """
    Generate a standardized failure response for API endpoints.

    Args:
        message (str): A message describing the failure or error.
        errors (APIValidationErrors): The validation errors or details of the failure.
        status (int, optional): The HTTP status code for the response. Defaults to 404.
        headers (Optional[dict[str, str]], optional): Additional headers to include in the response. Defaults to None.
        exception (bool, optional): Whether the response is an exception response. Defaults to False.
        content_type (Optional[str], optional): The content type of the response. Defaults to None.

    Example:
        ```python
        response = failure_response(
            message="Resource not found.",
            data={"detail": "The requested resource does not exist."},
            status=404
        )
        ```

    Returns:
        Response object with formatted data in the structure:
        {
            "message": str,
            "data": {"detail": "The requested resource does not exist."}
        }
    """
    return Response(
        message=message,
        data=errors,
        status=status,
        headers=headers,
        exception=exception,
        content_type=content_type,
    )
