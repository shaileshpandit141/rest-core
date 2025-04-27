import logging
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string
from smtplib import SMTPException
from typing import Any, Callable
from .models import Emails, Templates

# Set up logger
logger = logging.getLogger(__name__)


class EmailsError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TemplatesError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class SendEmailCredentialsValidator:
    def validate(
        self,
        data: Any,
        excepted_data_class: Any,
        exception_class: Callable,
        message: str,
    ) -> None:
        if not isinstance(data, excepted_data_class):
            raise exception_class(message)


class SendEmail:
    def __init__(
        self,
        subject: str,
        emails: Emails,
        context: dict[str, Any],
        templates: Templates,
    ) -> None:
        # validate all email credentials
        validator = SendEmailCredentialsValidator()
        validator.validate(
            data=emails,
            excepted_data_class=Emails,
            exception_class=EmailsError,
            message="Invalid emails credentials",
        )

        validator.validate(
            data=context,
            excepted_data_class=dict,
            exception_class=TypeError,
            message="Invalid context credentials",
        )

        validator.validate(
            data=templates,
            excepted_data_class=Templates,
            exception_class=TemplatesError,
            message="Invalid templates credentials",
        )

        self.subject = subject
        self.emails = emails
        self.context = context
        self.templates = templates

        # State variable definition.
        self.successful_email_send: list[str] = []
        self.fallback_successful_email_send: list[str] = []

        self._validate_templates()
        self.unique_to_emails = self._get_unique_to_emails()

    def send(self) -> None:
        """Main method to send the email."""
        try:
            self._send_email()
        except (SMTPException, ValidationError) as error:
            logger.error(f"Error sending email to {self.unique_to_emails}: {error}")
            self._send_fallback_email()
        except Exception as error:
            logger.exception(f"Unexpected error while sending email: {error}")
            self._send_fallback_email()

    def _is_valid_email(self, email: str) -> bool:
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def _get_unique_to_emails(self) -> list[str]:
        processed_emails = []
        for email in self.emails.to_emails:
            valid_email = email if self._is_valid_email(email) else self.emails.from_email
            if valid_email not in processed_emails:
                processed_emails.append(valid_email)
        return processed_emails

    def _validate_templates(self) -> None:
        if not self.templates.text_template.endswith(".txt"):
            raise ValidationError("Text template must end with '.txt'")
        if not self.templates.html_template.endswith(".html"):
            raise ValidationError("HTML template must end with '.html'")

    def _render_templates(self) -> tuple[str, str]:
        text_content = render_to_string(self.templates.text_template, self.context)
        html_content = render_to_string(self.templates.html_template, self.context)
        return text_content, html_content

    def _send_email(self) -> None:
        text_content, html_content = self._render_templates()

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=text_content,
            from_email=self.emails.from_email,
            to=self.unique_to_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        self.successful_email_send = self.unique_to_emails
        logger.info(f"Email sent successfully to: {', '.join(self.unique_to_emails)}")

    def _send_fallback_email(self) -> None:
        try:
            text_content, html_content = self._render_templates()

            fallback_email = EmailMultiAlternatives(
                subject=self.subject,
                body=text_content,
                from_email=self.emails.from_email,
                to=self.emails.from_email,
            )
            fallback_email.attach_alternative(html_content, "text/html")
            fallback_email.send()

            self.fallback_successful_email_send = [self.emails.from_email]  # type: ignore
            logger.info(f"Fallback email sent to: {self.emails.from_email}")

        except Exception as error:
            logger.error(f"Error sending fallback email: {error}")


SendEmail(
    subject="some email subject",
    emails=Emails(from_email="my@gmail.com", to_emails=["to@gmail.com"]),
    context={},
    templates=Templates(
        text_template="/templates/email.txt", html_template="/templates/email.html"
    ),
)
