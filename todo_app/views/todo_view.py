from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from rest_core.pagination import get_paginated_data
from rest_core.response import Response, failure_response, success_response

from ..models import Todo
from ..serializers import TodoSerializer


class TodoListAPIView(APIView):
    """Todo list view to handle GET and POST requests."""

    # Set throttle for this view.
    throttle_classes = [UserRateThrottle]

    def get(self, request) -> Response:
        """Handle GET request and return list of todo."""

        # Query all todos from db.
        queryset = Todo.objects.all()

        # Paginate and serializer featched queryset.
        paginated_data = get_paginated_data(request, queryset, TodoSerializer)

        # Return success respone with paginated data.
        return success_response(
            message="Todo retrive request wass successfull",
            data=paginated_data,
        )

    def post(self, request) -> Response:
        """Handle POST request for todos creation."""

        # Serializer request data with todo serializer
        serializer = TodoSerializer(
            data=request.data, many=isinstance(request.data, list)
        )

        # Check serializer is valid or not
        if serializer.is_valid():
            serializer.save(user=request.user)
            return success_response(
                message="Todo created successfully",
                data=serializer.data,
            )
        return failure_response(
            message="Todo creation failed",
            errors=serializer.errors,
        )


class TodoDetailAPIView(APIView):
    """Todo detail view to handle GET, PUT and DELETE requests."""

    # Set throttle for this view.
    throttle_classes = [UserRateThrottle]

    def get_object(self, todo_id: int) -> Todo | None:
        """Get todo object by id."""
        try:
            return Todo.objects.get(id=todo_id)
        except Todo.DoesNotExist:
            return None

    def get(self, request, todo_id: int) -> Response:
        """Handle GET request for todo detail."""
        todo = self.get_object(todo_id)
        if todo:
            serializer = TodoSerializer(todo)
            return success_response(
                message="Todo retrive request wass successfull",
                data=serializer.data,
            )
        return failure_response(
            message="Todo not found",
            errors={"todo": ["Todo with this id does not exist"]},
            status=status.HTTP_404_NOT_FOUND,
        )

    def put(self, request, todo_id: int) -> Response:
        """Handle PUT request for todo update."""
        todo = self.get_object(todo_id)
        if not todo:
            return failure_response(
                message="Todo not found",
                errors={"todo": ["Todo with this id does not exist"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serializer request data with todo serializer
        serializer = TodoSerializer(
            instance=todo, data=request.data
        )

        # Check serializer is valid or not
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Todo updated successfully",
                data=serializer.data,
            )
        return failure_response(
            message="Todo update failed",
            errors=serializer.errors,
        )

    def patch(self, request, todo_id: int) -> Response:
        """Handle PATCH request for partial todo update."""
        todo = self.get_object(todo_id)
        if not todo:
            return failure_response(
                message="Todo not found",
                errors={"todo": ["Todo with this id does not exist"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serializer request data with todo serializer
        serializer = TodoSerializer(instance=todo, data=request.data, partial=True)

        # Check serializer is valid or not
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Todo updated successfully",
                data=serializer.data,
            )
        return failure_response(
            message="Todo update failed",
            errors=serializer.errors,
        )

    def delete(self, request, todo_id: int) -> Response:
        """Handle DELETE request for todo delete."""
        todo = self.get_object(todo_id)
        if not todo:
            return failure_response(
                message="Todo not found",
                errors={"todo": ["Todo with this id does not exist"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Delete todo object
        todo.delete()
        return success_response(
            message="Todo deleted successfully",
            data={},
        )
