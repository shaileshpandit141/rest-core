import logging
from typing import Any, Optional, Type

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from rest_framework.serializers import Field

logger = logging.getLogger(__name__)


class RecordsCreationMixin:
    Meta: Optional[Type] = None
    file_fields: list[str] | None = None

    def create(self, validated_data) -> Any:
        logger.debug(f"Starting creation with validated_data: {validated_data}")
        extra_fields = self.context.get("extra_fields", {})  # type: ignore
        logger.debug(f"Extra fields from context: {extra_fields}")

        model = getattr(self.Meta, "model", None)
        if model is None:
            logger.error("Meta.model not defined.")
            raise AttributeError(f"{self.__class__.__name__} missing Meta.model.")

        valid_extra_fields = {
            k: v for k, v in extra_fields.items() if hasattr(model, k)
        }
        logger.debug(f"Valid extra fields: {valid_extra_fields}")

        if isinstance(validated_data, list):
            instances = [model(**valid_extra_fields, **item) for item in validated_data]
            if instances:
                logger.info(
                    f"Bulk creating {len(instances)} {model.__name__} instances."
                )
                return model.objects.bulk_create(instances)
            logger.info("No instances to create.")
            return []

        logger.info(f"Creating a single instance of {model.__name__}")
        return super().create({**valid_extra_fields, **validated_data})  # type: ignore

    def get_fields(self) -> dict[str, Field]:
        fields = super().get_fields()  # type: ignore
        meta = getattr(self, "Meta", None)
        model: Optional[Type[Model]] = getattr(meta, "model", None)

        if model is None:
            raise ValueError("Meta.model must be defined.")

        logger.debug(f"Setting up fields for {model.__name__}")

        for field_name, field in fields.items():
            try:
                model_field = model._meta.get_field(field_name)  # type: ignore
                if hasattr(model_field, "error_messages"):
                    field.error_messages.update(model_field.error_messages)
            except FieldDoesNotExist:
                logger.debug(f"Skipping unknown field '{field_name}'")

        return fields
