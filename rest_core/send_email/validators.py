from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class EmailValidator:
    @staticmethod
    def is_valid(email: str | None) -> bool:
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    @staticmethod
    def validate_templates(text_template: str, html_template: str) -> None:
        if not text_template.endswith(".txt"):
            raise ValidationError("Text template must end with '.txt'")
        if not html_template.endswith(".html"):
            raise ValidationError("HTML template must end with '.html'")
