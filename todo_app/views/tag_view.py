from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from rest_core.pagination import get_paginated_data
from rest_core.response import Response, failure_response, success_response

from ..models import Tag
from ..serializers import TagSerializer


class TagListAPIView(APIView):
    """Tag list view to handle GET and POST requests."""

    # Set throttle for this view.
    throttle_classes = [UserRateThrottle]

    def get(self, request) -> Response:
        """Handle GET request and return list of tag."""

        # Query all tags from db.
        queryset = Tag.objects.all()

        # Paginate and serializer featched queryset.
        paginated_data = get_paginated_data(request, queryset, TagSerializer)

        # Return success respone with paginated data.
        return success_response(
            message="Tag retrive request wass successfull",
            data=paginated_data,
        )

    def post(self, request) -> Response:
        """Handle POST request for tags creation."""

        # Serializer request data with tag serializer
        serializer = TagSerializer(
            data=request.data, many=isinstance(request.data, list)
        )

        # Check serializer is valid or not
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Tag created successfully",
                data=serializer.data,
            )
        return failure_response(
            message="Tag creation failed",
            errors=serializer.errors,
        )


class TagDetailAPIView(APIView):
    """Tag detail view to handle GET, PUT and DELETE requests."""

    # Set throttle for this view.
    throttle_classes = [UserRateThrottle]

    def get_object(self, tag_id: int) -> Tag | None:
        """Get tag object by id."""

        try:
            return Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return None

    def get(self, request, tag_id: int) -> Response:
        """Handle GET request for tag detail."""

        # Get tag object by id.
        tag = self.get_object(tag_id)
        if not tag:
            return failure_response(
                message="Tag not found",
                errors={"tag": ["Tag with this id does not exist."]},
            )

        # Serialize tag data.
        serializer = TagSerializer(tag)

        # Return success response with serialized data.
        return success_response(
            message="Tag retrive request wass successfull",
            data=serializer.data,
        )

    def put(self, request, tag_id: int) -> Response:
        """Handle PUT request for tag update."""

        # Get tag object by id.
        tag = self.get_object(tag_id)
        if not tag:
            return failure_response(
                message="Tag not found",
                errors={"tag": ["Tag with this id does not exist."]},
            )

        # Serializer request data with tag serializer
        serializer = TagSerializer(tag, data=request.data)

        # Check serializer is valid or not
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Tag updated successfully",
                data=serializer.data,
            )
        return failure_response(
            message="Tag update failed",
            errors=serializer.errors,
        )
    
    def patch(self, request, tag_id: int) -> Response:
        """Handle PATCH request for partial tag update."""

        # Get tag object by id.
        tag = self.get_object(tag_id)
        if not tag:
            return failure_response(
                message="Tag not found",
                errors={"tag": ["Tag with this id does not exist."]},
            )

        # Serializer request data with tag serializer
        serializer = TagSerializer(tag, data=request.data, partial=True)

        # Check serializer is valid or not
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Tag updated successfully",
                data=serializer.data,
            )
        return failure_response(
            message="Tag update failed",
            errors=serializer.errors,
        )

    def delete(self, request, tag_id: int) -> Response:
        """Handle DELETE request for tag deletion."""

        # Get tag object by id.
        tag = self.get_object(tag_id)
        if not tag:
            return failure_response(
                message="Tag not found",
                errors={"tag": ["Tag with this id does not exist."]},
            )

        # Delete tag object.
        tag.delete()

        # Return success response.
        return success_response(
            message="Tag deleted successfully",
            data={},
            status=status.HTTP_204_NO_CONTENT,
        )
