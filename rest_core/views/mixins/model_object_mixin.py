from typing import TypeVar, Any, Type, Generic
from django.db.models import Model

# Define a generic type variable bound to Django Model
TypeModel = TypeVar("TypeModel", bound=Model)


class ModelAttributeNotFound(Exception): ...


class ModelObjectMixin(Generic[TypeModel]):
    """
    Mixin to provide a method for retrieving a model object by its attributes.
    This mixin is intended to be used in Django views or viewsets.
    It requires the `model` attribute to be set in the class that inherits from this mixin.

    Example usage:
    ```
        class MyView(ModelObjectMixin[Book], APIView):
            model = Book
            def get(self, request, *args, **kwargs) -> JsonResponse:
                # Use the mixin's method to get an object by id
                obj = self.get_object(id=1)
                if obj is None:
                    return JsonResponse({"error": "Object not found"}, status=404)
                # Do something with the object
                return JsonResponse(obj.to_dict())
    ```
    """

    model: Type[TypeModel] | None = None

    def get_object(self, **kwargs: Any) -> TypeModel | None:
        """
        Retrieve a model object based on the provided keyword arguments.
        If the object does not exist, return None.

        param kwargs:
            - Keyword arguments to filter the model object.
        return:
            - The model object if found, otherwise None.
        raise ModelAttributeNotFound:
            - If the model attribute is not set in the class.
        raise self.model.DoesNotExist:
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
        # Check if the model attribute is set
        if self.model is None:
            raise ModelAttributeNotFound("Model attribute is not set in the class.")

        # Attempt to retrieve the object using the provided keyword arguments
        try:
            return self.model.objects.get(**kwargs)
        except self.model.DoesNotExist:
            return None
