from typing import Optional, Sequence, Any
from urllib.parse import urlencode
from django.urls import reverse
from django.http import HttpRequest
from rest_framework.request import Request


def build_absolute_uri(
    request: HttpRequest | Request,
    view_name: str,
    args: Optional[Sequence[Any]] = None,
    kwargs: Optional[dict[str, Any]] = None,
    query_params: Optional[dict[str, Any]] = None,
) -> str:
    """
    Build an absolute URI for the given view name, including optional query parameters.

    Args:
        request: Django or DRF request object.
        view_name: Name of the URL pattern to reverse.
        args: Optional positional arguments for the URL.
        kwargs: Optional keyword arguments for the URL.
        query_params: Optional dictionary of query parameters.

    Returns:
        Absolute URI as a string.
    """
    relative_url = reverse(view_name, args=args, kwargs=kwargs)

    if query_params:
        query_string = urlencode(query_params, doseq=True)
        relative_url = f"{relative_url}?{query_string}"

    return request.build_absolute_uri(relative_url)
