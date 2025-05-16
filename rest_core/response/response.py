from typing import Optional

from rest_framework.response import Response as Response

from .types import APIResponseData, APIValidationErrors


class APIResponseBuilder:
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
        Build the API response object.

        Returns:
            Response: A Django Rest Framework Response object with the specified attributes.
        """
        # Create the response object using Django Rest Framework's Response class
        response = Response(
            data=self.data,
            status=self.status,
            headers=self.headers,
            exception=self.exception,
            content_type=self.content_type,
        )

        # Update the response status text as for message
        if self.message:
            setattr(response, "status_text", self.message)

        # Finally return the response object
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
    # Create the APIResponseBuilder instance
    response_builder = APIResponseBuilder(
        message=message,
        data=data,
        status=status,
        headers=headers,
        exception=exception,
        content_type=content_type,
    )
    # Build the response object
    response = response_builder.build()

    # Finally return the response object
    return response


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
    # Create the APIResponseBuilder instance
    response_builder = APIResponseBuilder(
        message=message,
        data=errors,
        status=status,
        headers=headers,
        exception=exception,
        content_type=content_type,
    )
    # Build the response object
    response = response_builder.build()

    # Finally return the response object
    return response


def destroy_response() -> Response:
    """
    Generate a standardized response for successful deletion operations.
    """
    # Create the APIResponseBuilder instance
    response_builder = APIResponseBuilder(
        message=None,
        data=None,
        status=204,
        headers=None,
        exception=False,
        content_type=None,
    )
    # Build the response object
    response = response_builder.build()

    # Finally return the response object
    return response
