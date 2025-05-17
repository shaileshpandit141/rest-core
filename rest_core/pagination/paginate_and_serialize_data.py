from logging import getLogger
from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer, Serializer

from .page_number_pagination import PageNumberPagination

logger = getLogger(__name__)


def paginate_and_serialize_data(
    request: HttpRequest | Request,
    queryset: QuerySet,
    serializer_class: type[Serializer | ModelSerializer],
) -> dict[str, Any]:
    """
    Paginate and serialize a Django QuerySet using a custom PageNumberPagination class.

    Args:
        request (HttpRequest | Request): The incoming HTTP request.
        queryset (QuerySet): QuerySet to paginate.
        serializer_class (type): Serializer class to serialize the paginated data.

    Returns:
        dict[str, Any]: A dictionary with pagination metadata and serialized results:
            {
                "page": {
                    "current": int,
                    "total": int,
                    "size": int,
                    "total_items": int,
                    "next": str | None,
                    "previous": str | None,
                },
                "results": list
            }

    Raises:
        NotFound: If the requested page does not exist or yields no data.
    """
    logger.debug("Starting pagination with custom PageNumberPagination.")
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)

    if page is None:
        logger.warning("No data returned from pagination. Possibly invalid page.")
        raise NotFound("The requested records were not found.")

    serializer = serializer_class(
        instance=page,
        many=True,
        context={"request": request},
    )
    page_size = paginator.get_page_size(request)

    response_data = {
        "page": {
            "current": paginator.page.number,
            "total": paginator.page.paginator.num_pages,
            "size": page_size,
            "total_items": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
        },
        "results": serializer.data,
    }

    logger.debug(f"Pagination result: {response_data}")
    return response_data
