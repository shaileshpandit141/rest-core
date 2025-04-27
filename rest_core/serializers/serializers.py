from rest_framework.serializers import (
    Field,
    ModelSerializer as DrfModelSerializer,
    Serializer as DrfSerializer
)
from typing import Any, Optional, Type
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
import logging

logger = logging.getLogger(__name__)


class Serializer(DrfSerializer):
    Meta: Optional[Type]
    file_fields: list[str] | None = None

    def create(self, validated_data) -> Any:
        """
        Create a new instance or instances of the model using the validated data.

        This method extracts extra fields from the context, filters out any invalid ones based
        on the model's attributes, and supports both single and bulk creation. In the case of
        bulk creation, it uses Django's bulk_create to efficiently create multiple instances.

        Args:
            validated_data (dict or list): The validated data for creating the model instance(s).

        Returns:
            Any: A single model instance or a list of created instances.

        Raises:
            AttributeError: If Meta.model is not defined.
        """
        logger.debug(
            f"Starting creation of model instance(s) with validated_data: {validated_data}"
        )
        # Get extra fields from context (default to empty dict)
        extra_fields = self.context.get("extra_fields", {})
        logger.debug(f"Extra fields retrieved from context: {extra_fields}")

        # Get model instance from Meta class
        model = getattr(self.Meta, "model", None)
        if model is None:
            logger.error("Meta.model is not defined in the serializer.")
            raise AttributeError(
                f"{self.__class__.__name__} is missing a Meta.model definition."
            )

        # Ensure extra fields only contain valid model fields
        valid_extra_fields = {
            k: v for k, v in extra_fields.items() if hasattr(model, k)
        }
        logger.debug(f"Valid extra fields after filtering: {valid_extra_fields}")

        # Handle bulk creation when validated_data is a list
        if isinstance(validated_data, list):
            instances = [model(**valid_extra_fields, **item) for item in validated_data]
            if instances:  # Prevent bulk_create error on an empty list
                logger.info(
                    f"Bulk creating {len(instances)} instances of {model.__name__}"
                )
                return model.objects.bulk_create(instances)
            logger.info("No instances to create in bulk; returning an empty list.")
            return []  # Return an empty list if no instances were created

        # Default single object creation
        logger.info(f"Creating a single instance of {model.__name__}")
        return super().create({**valid_extra_fields, **validated_data})

    def get_fields(self) -> dict[str, Field]:
        fields = super().get_fields()
        meta = getattr(self, "Meta", None)
        model: Optional[Type[Model]] = getattr(meta, "model", None)

        if model is None:
            raise ValueError("Meta.model must be defined in subclasses.")

        logger.debug(f"Initializing fields for model: {model.__name__}")

        for field_name, field in fields.items():
            try:
                model_field = model._meta.get_field(field_name)
                if hasattr(model_field, "error_messages"):
                    logger.debug(f"Updating error messages for field: {field_name}")
                    field.error_messages.update(model_field.error_messages)
            except FieldDoesNotExist:
                logger.debug(
                    f"Field '{field_name}' does not exist on model '{model.__name__}'; skipping.",
                )
                pass  # Ignore non-model fields

        return fields

    def to_representation(self, instance) -> dict:
        representation = super().to_representation(instance)

        # If the serializer also inherits from FileUrlMixin, enhance files
        if hasattr(self, "enhance_file_fields"):
            representation = self.enhance_file_fields(instance, representation)

        return representation


class ModelSerializer(DrfModelSerializer):
    Meta: Optional[Type]

    def create(self, validated_data) -> Any:
        """
        Create a new instance or instances of the model using the validated data.

        This method extracts extra fields from the context, filters out any invalid ones based
        on the model's attributes, and supports both single and bulk creation. In the case of
        bulk creation, it uses Django's bulk_create to efficiently create multiple instances.

        Args:
            validated_data (dict or list): The validated data for creating the model instance(s).

        Returns:
            Any: A single model instance or a list of created instances.

        Raises:
            AttributeError: If Meta.model is not defined.
        """
        logger.debug(
            f"Starting creation of model instance(s) with validated_data: {validated_data}"
        )
        # Get extra fields from context (default to empty dict)
        extra_fields = self.context.get("extra_fields", {})
        logger.debug(f"Extra fields retrieved from context: {extra_fields}")

        # Get model instance from Meta class
        model = getattr(self.Meta, "model", None)
        if model is None:
            logger.error("Meta.model is not defined in the serializer.")
            raise AttributeError(
                f"{self.__class__.__name__} is missing a Meta.model definition."
            )

        # Ensure extra fields only contain valid model fields
        valid_extra_fields = {
            k: v for k, v in extra_fields.items() if hasattr(model, k)
        }
        logger.debug(f"Valid extra fields after filtering: {valid_extra_fields}")

        # Handle bulk creation when validated_data is a list
        if isinstance(validated_data, list):
            instances = [model(**valid_extra_fields, **item) for item in validated_data]
            if instances:  # Prevent bulk_create error on an empty list
                logger.info(
                    f"Bulk creating {len(instances)} instances of {model.__name__}"
                )
                return model.objects.bulk_create(instances)
            logger.info("No instances to create in bulk; returning an empty list.")
            return []  # Return an empty list if no instances were created

        # Default single object creation
        logger.info(f"Creating a single instance of {model.__name__}")
        return super().create({**valid_extra_fields, **validated_data})

    def get_fields(self) -> dict[str, Field]:
        fields = super().get_fields()
        meta = getattr(self, "Meta", None)
        model: Optional[Type[Model]] = getattr(meta, "model", None)

        if model is None:
            raise ValueError("Meta.model must be defined in subclasses.")

        logger.debug(f"Initializing fields for model: {model.__name__}")

        for field_name, field in fields.items():
            try:
                model_field = model._meta.get_field(field_name)
                if hasattr(model_field, "error_messages"):
                    logger.debug(f"Updating error messages for field: {field_name}")
                    field.error_messages.update(model_field.error_messages)
            except FieldDoesNotExist:
                logger.debug(
                    f"Field '{field_name}' does not exist on model '{model.__name__}'; skipping.",
                )
                pass  # Ignore non-model fields

        return fields

    def to_representation(self, instance) -> dict:
        representation = super().to_representation(instance)

        # If the serializer also inherits from FileUrlMixin, enhance files
        if hasattr(self, "enhance_file_fields"):
            representation = self.enhance_file_fields(instance, representation)

        return representation

