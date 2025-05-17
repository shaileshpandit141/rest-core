from rest_framework.response import Response
from rest_framework.views import APIView

from ..response import success_response
from .mixins import ModelChoiceFieldMixin


class ModelChoiceFieldAPIView(ModelChoiceFieldMixin, APIView):
    """
    API view to retrieve choice fields from a Django model.
    Inherits from ModelChoiceFieldMixin and APIView.
    """

    def get(self, request) -> Response:
        """
        Handle GET requests to retrieve choice fields.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A JSON response containing the choice fields.
        """

        # Get the choice fields from the mixin
        choice_fields = self.get_choice_fields()

        # Return a success response with the choice fields
        return success_response(
            message=f"{self.model.__name__} choice fields retrieved successfully",
            data=choice_fields,
        )
