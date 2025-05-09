from rest_framework.pagination import PageNumberPagination as DrfPageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(DrfPageNumberPagination):
    """
    A custom pagination class extending DRF's PageNumberPagination that allows clients
    to set the page size via a query parameter ("page-size") and provides a detailed
    paginated response.

    Attributes:
        page_size_query_param (str): The query parameter name used to dynamically set the
            number of items per page.

    Methods:
        get_paginated_response(data):
            Constructs and returns an HTTP response containing pagination details and the
            paginated data. The response includes information about the current page, total
            number of pages, total items, items per page, navigation flags (has_next, has_previous),
            next and previous page numbers (if applicable), as well as next and previous page links.

    Args (for get_paginated_response):
        data (list): The list of serialized items for the current page.

    Returns (from get_paginated_response):
        Response: A response object containing:
            - current_page (int): Current page number.
            - total_pages (int): Total number of pages available.
            - total_items (int): Total number of items across all pages.
            - items_per_page (int): Number of items displayed per page.
            - has_next (bool): Indicates if there is a subsequent page.
            - has_previous (bool): Indicates if there is a previous page.
            - next_page_number (int or None): Next page number if available, else None.
            - previous_page_number (int or None): Previous page number if available, else None.
            - next (str): URL for the next page.
            - previous (str): URL for the previous page.
            - results (list): The paginated data provided.
    """

    # Allow clients to set page size via query param
    page_size_query_param = "page-size"

    def get_paginated_response(self, data) -> Response:
        page = self.page
        paginator = self.page.paginator
        items_per_page = self.get_page_size(self.request)

        return Response(
            {
                "current_page": page.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "items_per_page": items_per_page,
                "has_next": page.has_next(),
                "has_previous": page.has_previous(),
                "next_page_number": (
                    page.next_page_number() if page.has_next() else None
                ),
                "previous_page_number": (
                    page.previous_page_number() if page.has_previous() else None
                ),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
