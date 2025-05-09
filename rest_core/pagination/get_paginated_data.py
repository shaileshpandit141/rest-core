from logging import getLogger
from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer, Serializer

from .page_number_pagination import PageNumberPagination

logger = getLogger(__name__)


def get_paginated_data(
    request: HttpRequest | Request,
    queryset: QuerySet,
    serializer_class: type[Serializer | ModelSerializer],
) -> dict[str, Any]:
    """
    Retrieves paginated data from a given QuerySet using the custom PageNumberPagination class.

    This function takes an incoming request and a QuerySet, paginates the QuerySet according to
    the pagination settings (default page 1 and 10 items per page, configurable), and returns a dictionary
    with detailed pagination information along with the serialized queryset data.

    Parameters:
        request (HttpRequest | Request): The incoming HTTP request object. This can be either a Django
            HttpRequest or a DRF Request.
        queryset (QuerySet): The Django QuerySet containing records to paginate.
        serializer_class (type[Serializer | ModelSerializer]): The serializer class used to serialize each
            item of the paginated queryset. Accepts both base Serializer and ModelSerializer subclasses.

    Returns:
        dict[str, Any]: A dictionary containing the paginated data with the following keys:
            - "current_page": Current page number.
            - "total_pages": Total number of pages.
            - "total_items": Total count of items in the queryset.
            - "items_per_page": Number of items displayed per page.
            - "has_next": Boolean flag indicating if there is a next page.
            - "has_previous": Boolean flag indicating if there is a previous page.
            - "next_page_number": The next page number if available, otherwise None.
            - "previous_page_number": The previous page number if available, otherwise None.
            - "next": URL link to the next page if available, otherwise None.
            - "previous": URL link to the previous page if available, otherwise None.
            - "results": Serialized data of the current page.

    Raises:
        NotFound: If the paginator does not return any data (i.e., the page is None), indicating that the requested
            records were not found.

    Notes:
        - The function uses a custom pagination class (PageNumberPagination), which is imported from '.page_number_pagination'.
        - Debug and warning logs are generated to help trace the pagination process.
    """
    logger.debug("Starting pagination process using pagination_class.")
    paginator = PageNumberPagination()

    page = paginator.paginate_queryset(queryset, request)
    if page is None:
        logger.warning("Paginated page is None. Records not found.")
        raise NotFound("The requested records were not found.")

    serializer = serializer_class(instance=page, many=True)
    page_size = paginator.get_page_size(request)

    result = {
        "current_page": paginator.page.number,
        "total_pages": paginator.page.paginator.num_pages,
        "total_items": paginator.page.paginator.count,
        "items_per_page": page_size,
        "has_next": paginator.page.has_next(),
        "has_previous": paginator.page.has_previous(),
        "next_page_number": (
            paginator.page.next_page_number() if paginator.page.has_next() else None
        ),
        "previous_page_number": (
            paginator.page.previous_page_number()
            if paginator.page.has_previous()
            else None
        ),
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "results": serializer.data,
    }

    logger.debug(f"Pagination data calculated: {result}")
    return result
