import logging

from django.db import models

logger = logging.getLogger(__name__)


class FileUrlMixin:
    """
    A mixin that updates FileField and ImageField URLs in serializer output
    to be absolute URLs, compatible with cloud storage backends.
    """

    # manually specify file fields for non-model serializers
    file_fields: list[str] | None = None

    def to_representation(self, instance):
        # Call the serializer's normal representation
        representation = super().to_representation(instance)  # type: ignore
        return self.enhance_file_fields(instance, representation)

    def enhance_file_fields(self, instance, representation: dict) -> dict:
        """
        Enhances file and image fields in the representation with absolute URLs.

        Args:
            instance: The model instance or raw data object.
            representation: The initial serialized representation.

        Returns:
            dict: The updated representation.
        """
        request = self.context.get("request", None)  # type: ignore

        # Detect file fields
        model_fields = {}
        if hasattr(instance, "_meta"):  # ModelSerializer case
            model_fields = {field.name: field for field in instance._meta.get_fields()}

        manual_fields = getattr(self, "file_fields", []) or []

        for field_name, field_value in representation.items():
            model_field = model_fields.get(field_name)

            is_file_field = (
                isinstance(model_field, (models.FileField, models.ImageField))
                or field_name in manual_fields
            )

            if not is_file_field:
                continue

            try:
                # ModelSerializer: use instance field
                if model_field:
                    file_instance = getattr(instance, field_name, None)
                    file_url = (
                        getattr(file_instance, "url", None) if file_instance else None
                    )
                else:
                    # Normal Serializer: assume the value itself is the URL or path
                    file_url = field_value

                if file_url:
                    if request:
                        file_url = request.build_absolute_uri(file_url)
                    representation[field_name] = file_url
                    logger.debug(f"Enhanced URL for {field_name}: {file_url}")
                else:
                    representation[field_name] = None
                    logger.info(f"No file found for field: {field_name}")

            except Exception as error:
                logger.error(
                    f"Unexpected error processing file field {field_name}: {error}"
                )

        return representation
