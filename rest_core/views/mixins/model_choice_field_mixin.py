from typing import Iterable, Tuple, cast

from django.db.models import Model


class ModelAttributeNotFound(Exception):
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


class ModelChoiceFieldMixin:
    """Mixin to retrieve choice fields from a Django model."""

    model: type[Model] | None = None
    choice_fields: list[str] | None = None

    def get_choice_fields(self) -> dict[str, dict[str, str]]:
        """
        Retrieve the choice fields from the queryset model class.

        Returns:
            dict[str, dict[str, str]]: A dictionary where keys are field names
            and values are dictionaries of choices (value => label).

        Raises:
            ModelAttributeNotFound: If the model attribute is not set.
            ChoiceFiledAttributeNotFound: If the choice_fields attribute is not set.
            ChoiceFieldNotFound: If any specified field does not exist or has no choices.
        """

        if self.model is None:
            raise ModelAttributeNotFound("Model attribute is not set in the class.")

        if self.choice_fields is None:
            raise ChoiceFiledAttributeNotFound(
                "The choice_fields attribute must be set in the class."
            )

        # Define a dictionary to hold the choices
        choices_as_dict: dict[str, dict[str, str]] = {}

        # Iterate over the choice fields and retrieve their choices
        for field in self.choice_fields:
            try:
                field_obj = self.model._meta.get_field(field)
                raw_choices = cast(Iterable[Tuple[str, str]], field_obj.choices or [])
                choices_as_dict[field] = dict(raw_choices)
            except Exception:
                raise ChoiceFieldNotFound(
                    f"The field '{field}' is not found or has no choices in the model '{self.model.__name__}'."
                )

        # Return the choices as a dictionary
        return choices_as_dict
