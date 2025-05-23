from django.http import JsonResponse


def url_404_apiview(request, exception) -> JsonResponse:
    """
    Custom 404 error handler that returns a JSON response when a
    page/endpoint is not found.
    """
    return JsonResponse(
        {
            "status": "failed",
            "status_code": 404,
            "message": "This endpoint does not exist.",
            "data": None,
            "errors": {
                "detail": "The requested endpoint could not be found.",
                "code": "not_found",
            },
            "meta": {},
        },
        status=404,
    )
