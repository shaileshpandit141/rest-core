import logging
from typing import Iterable, Tuple, cast

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from rest_core.response import failure_response, success_response
from rest_core.viewsets.mixins import ActionMessageMixin

# Configure logger for this module
logger = logging.getLogger(__name__)


class ChoiceFieldNotFound(Exception):
    """Raised when a specified field does not exist or has no choices."""

    pass


class ChoiceFieldViewSetMixin(ActionMessageMixin):
    """
    Mixin to expose a `choice-fields/` endpoint on a DRF ViewSet.
    Automatically gets the model from the queryset.
    """

    choice_fields: list[str] = []

    def get_model(self) -> type[Model]:
        """
        Retrieves the model class from the queryset.
        """
        try:
            model = self.get_queryset().model  # type: ignore[return-value]
            logger.debug(f"Inferred model from queryset: {model}")
            return model
        except (AttributeError, AssertionError) as e:
            logger.exception("Failed to infer model from queryset.")
            raise RuntimeError(
                "Could not infer model from queryset. Ensure 'queryset' is set."
            ) from e

    def get_choice_fields(self) -> dict[str, dict[str, str]]:
        """
        Extracts choice fields from the model.
        Returns:
            A dictionary mapping field names to their available choices.
        """
        if not self.choice_fields:
            logger.info("No `choice_fields` defined on the viewset.")
            return {}

        model = self.get_model()
        choices_as_dict: dict[str, dict[str, str]] = {}

        for field_name in self.choice_fields:
            try:
                field = model._meta.get_field(field_name)
                raw_choices = cast(Iterable[Tuple[str, str]], field.choices or [])
                if not raw_choices:
                    logger.warning(f"Field '{field_name}' has no choices.")
                    continue
                choices_as_dict[field_name] = dict(raw_choices)
                logger.debug(
                    f"Loaded choices for field '{field_name}': {choices_as_dict[field_name]}"
                )
            except FieldDoesNotExist:
                logger.error(
                    f"Field '{field_name}' does not exist on model '{model.__name__}'."
                )
                raise ChoiceFieldNotFound(
                    f"Field '{field_name}' does not exist on model '{model.__name__}'."
                )

        return choices_as_dict

    @action(detail=False, methods=["get"], url_path="choice-fields")
    def choice_fields_action(self, request: Request) -> Response:
        """
        DRF action that returns the configured choice fields in the model.
        Accessible via GET /<viewset-url>/choice-fields/
        """
        try:
            choices = self.get_choice_fields()

            if not choices:
                logger.info("No choice fields returned.")
                return success_response(
                    message="No choice fields found.",
                    data={"detail": "No choice fields found."},
                )

            logger.info("Choice fields retrieved successfully.")
            return success_response(
                message="Choice fields retrieved successfully.",
                data=choices,
            )

        except ChoiceFieldNotFound as e:
            logger.warning(f"Choice field retrieval failed: {e}")
            return failure_response(
                message="Choice retrieval failed.",
                errors={"detail": "Failed to retrieve choice fields."},
            )

        except Exception as e:
            logger.exception(
                f"Unexpected error during choice field retrieval. \nErrror: {e}"
            )
            return failure_response(
                message="Something went wrong. Please try again later.",
                errors={"detail": "An unexpected error occurred."},
            )
