from rest_framework.pagination import PageNumberPagination as DrfPageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(DrfPageNumberPagination):
    """
    A custom pagination class that extends DRF's PageNumberPagination with support for:
    - Dynamic page size via "page-size" query parameter.
    - Streamlined pagination metadata in a structured format.

    Attributes:
        page_size_query_param (str): The query parameter name to set page size dynamically.

    Methods:
        get_paginated_response(data):
            Returns a standardized paginated response structure.

    Response Structure:
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
    """

    # Allow clients to set page size via ?page-size=
    page_size_query_param = "page-size"

    def get_paginated_response(self, data) -> Response:
        page = self.page
        paginator = page.paginator
        items_per_page = self.get_page_size(self.request)

        return Response(
            {
                "page": {
                    "current": page.number,
                    "total": paginator.num_pages,
                    "size": items_per_page,
                    "total_items": paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )
