from typing import Optional

from rest_framework.response import Response

from .types import APIResponseData, APIValidationErrors


class APIResponseBuilder:
    """
    A helper class to construct a Django REST Framework Response object.
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
        self.message = message
        self.data = data
        self.status = status
        self.headers = headers
        self.exception = exception
        self.content_type = content_type

    def build(self) -> Response:
        """
        Build and return a DRF Response object with the given attributes.

        Returns:
            Response: Configured Django REST Framework Response object.
        """
        response = Response(
            data=self.data,
            status=self.status,
            headers=self.headers,
            exception=self.exception,
            content_type=self.content_type,
        )

        # Set the message as response attribute if provided
        if self.message:
            setattr(response, "message", self.message)

        # Return the constructed response object
        return response


def success_response(
    message: str,
    data: APIResponseData,
    status: int = 200,
    headers: Optional[dict[str, str]] = None,
    exception: bool = False,
    content_type: Optional[str] = None,
) -> Response:
    """
    Generate a standardized success response.

    Args:
        message (str): Success message.
        data (APIResponseData): Response payload.
        status (int): HTTP status code (default: 200).
        headers (dict[str, str], optional): Extra headers.
        exception (bool): Indicates an exception response.
        content_type (str, optional): Content type.

    Returns:
        Response: Structured success response with message and data.

    Example:
        ```python
        response = success_response(
            message="User created successfully.",
            data={"id": 1, "username": "john_doe"}
        )
        ```
    """
    return APIResponseBuilder(
        message=message,
        data=data,
        status=status,
        headers=headers,
        exception=exception,
        content_type=content_type,
    ).build()


def failure_response(
    message: str,
    errors: APIValidationErrors,
    status: int = 400,
    headers: Optional[dict[str, str]] = None,
    exception: bool = False,
    content_type: Optional[str] = None,
) -> Response:
    """
    Generate a standardized failure/error response.

    Args:
        message (str): Error message.
        errors (APIValidationErrors): Error or validation details.
        status (int): HTTP status code (default: 400).
        headers (dict[str, str], optional): Extra headers.
        exception (bool): Indicates an exception response.
        content_type (str, optional): Content type.

    Returns:
        Response: Structured error response with message and details.

    Example:
        ```python
        response = failure_response(
            message="Invalid input.",
            errors={"email": ["This field is required."]}
        )
        ```
    """
    return APIResponseBuilder(
        message=message,
        data=errors,
        status=status,
        headers=headers,
        exception=exception,
        content_type=content_type,
    ).build()


def destroy_response() -> Response:
    """
    Generate a standardized response for successful deletion.

    Returns:
        Response: Response with HTTP 204 No Content.
    """

    # Return the response object
    return APIResponseBuilder(status=204).build()
