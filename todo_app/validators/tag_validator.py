from django.core.exceptions import ValidationError


class TagValidators:
    """
    Provides validation methods related to the Tag model.
    """

    @staticmethod
    def validate_tag(tag: str) -> None:
        """
        Validates whether a tag with the given title exists.
        """
        # Lazy import of the Tag model
        from ..models import Tag

        # Check if the tag exists
        if not Tag.objects.filter(title=tag).exists():
            raise ValidationError(f"Invalid tag: '{tag}' does not exist.")
