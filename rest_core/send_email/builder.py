from django.template.loader import render_to_string
from typing import Any, Self

from .models import Emails, Templates
from .validators import EmailValidator


class EmailBuilder:
    def __init__(
        self,
        subject: str,
        emails: Emails,
        context: dict[str, Any],
        templates: Templates,
    ) -> None:
        self.subject = subject
        self.emails = emails
        self.context = context
        self.templates = templates
        self.text_body = ""
        self.html_body = ""

        self._validate()

    def _validate(self) -> None:
        EmailValidator.validate_templates(
            self.templates.text_template, self.templates.html_template
        )
        if not EmailValidator.is_valid(self.emails.from_email):
            raise ValueError("Invalid from_email")

    def build(self) -> Self:
        self.text_body = render_to_string(self.templates.text_template, self.context)
        self.html_body = render_to_string(self.templates.html_template, self.context)
        return self

    def get_data(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "text_body": self.text_body,
            "html_body": self.html_body,
            "from_email": self.emails.from_email,
            "to_emails": self.emails.to_emails,
        }
