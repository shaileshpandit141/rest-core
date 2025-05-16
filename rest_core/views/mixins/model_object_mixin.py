from typing import Any, Generic, TypeVar

from django.db.models import Model, QuerySet

# Define a generic type variable bound to Django Model
ModelType = TypeVar("ModelType", bound=Model)


class QuerysetAttributeNotFound(Exception):
    """
    Exception raised when the queryset attribute is not set in the class.
    This exception is used to indicate that the queryset attribute is required
    for the mixin to function properly.
    """

    ...


class ModelObjectMixin(Generic[ModelType]):
    """
    Mixin to provide a method for retrieving a model object by its attributes.
    This mixin is intended to be used in Django views or viewsets.
    It requires the `queryset` attribute to be set in the class that inherits from this mixin.

    Example usage:
    ```
        class MyView(ModelObjectMixin[Book], APIView):
            queryset = Book.objects.all()
            def get(self, request, *args, **kwargs) -> JsonResponse:
                # Use the mixin's method to get an object by id
                obj = self.get_object(id=1)
                if obj is None:
                    return JsonResponse({"error": "Object not found"}, status=404)
                # Do something with the object
                return JsonResponse(obj.to_dict())
    ```
    """

    queryset: QuerySet[ModelType] | None = None

    def get_object(self, **kwargs: Any) -> ModelType | None:
        """
        Retrieve a model object based on the provided keyword arguments.
        If the object does not exist, return None.

        param kwargs:
            - Keyword arguments to filter the model object.
        return:
            - The model object if found, otherwise None.
        raise QuerysetAttributeNotFound:
            - If the queryset attribute is not set in the class.
        raise self.queryset.model.DoesNotExist:
            - If the object does not exist in the database.
        Example usage:
        ```
            def get(self, request, *args, **kwargs) -> JsonResponse:
                # Use the mixin's method to get an object by id
                obj = self.get_object(id=1)
                if obj is None:
                    return JsonResponse({"error": "Object not found"}, status=404)
                # Do something with the object
                return JsonResponse(obj.to_dict())
        ```
        """
        # Check if the queryset attribute is set
        if self.queryset is None:
            raise QuerysetAttributeNotFound(
                "Queryset attribute is not set in the class."
            )

        # Attempt to retrieve the object using the provided keyword arguments
        try:
            return self.queryset.get(**kwargs)
        except self.queryset.model.DoesNotExist:
            return None
