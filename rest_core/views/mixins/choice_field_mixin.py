from typing import Generic, Iterable, Tuple, TypeVar, cast

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


class ChoiceFiledAttributeNotFound(Exception):
    """
    Exception raised when the choice fields attribute is not set in the class.
    This exception is used to indicate that the choice fields attribute is required
    for the mixin to function properly.
    """

    ...


class ChoiceFieldNotFound(Exception):
    """
    Exception raised when the choice field is not found in the queryset model.
    This exception is used to indicate that the choice field is required
    for the mixin to function properly.
    """

    ...


class ModelChoiceFiledMixin(Generic[ModelType]):
    queryset: QuerySet[ModelType] | None = None
    choice_fields: list[str] | None = None

    def get_choice_fields(self) -> dict[str, dict[str, str]]:
        """
        Retrieve the choice fields from the queryset model class.

        Returns:
            dict[str, dict[str, str]]: A dictionary where keys are field names
            and values are dictionaries of choices (value => label).

        Raises:
            QuerysetAttributeNotFound: If the queryset attribute is not set.
            ChoiceFiledsAttributeNotFound: If the choice_fields attribute is not set.
            ChoiceFieldNotFound: If any specified field does not exist or has no choices.
        """
        if self.queryset is None:
            raise QuerysetAttributeNotFound(
                "Queryset attribute is not set in the class."
            )

        if self.choice_fields is None:
            raise ChoiceFiledAttributeNotFound(
                "The choice_fields attribute must be set in the class."
            )

        model = self.queryset.model
        choices_as_dict: dict[str, dict[str, str]] = {}

        for field in self.choice_fields:
            try:
                field_obj = model._meta.get_field(field)
                raw_choices = cast(Iterable[Tuple[str, str]], field_obj.choices or [])
                choices_as_dict[field] = dict(raw_choices)
            except Exception:
                raise ChoiceFieldNotFound(
                    f"The field '{field}' is not found or has no choices in the model '{model.__name__}'."
                )

        # Return the choices as a dictionary
        return choices_as_dict
