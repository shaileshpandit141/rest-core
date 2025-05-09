import logging
from smtplib import SMTPException
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.template.loader import render_to_string

from .exceptions import EmailsError, TemplatesError
from .models import Emails, Templates
from .types import SendStatusTyped
from .validators import EmailServiceValidator

# Set up logger
logger = logging.getLogger(__name__)

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class EmailService:
    def __init__(
        self,
        subject: str,
        emails: Emails,
        context: dict[str, Any],
        templates: Templates,
    ) -> None:
        # validate all email credentials
        validator = EmailServiceValidator()
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

        self.from_email = emails.from_email or DEFAULT_FROM_EMAIL
        self.email_sends: list[str] = []
        self.fallback_email_sends: list[str] = []

        self._validate_templates()
        self.unique_to_emails = self._get_unique_to_emails()

        if not self.unique_to_emails:
            raise EmailsError("No valid recipient email addresses found.")

    def send(self, fallback: bool = True) -> SendStatusTyped:
        """Send email and optionally attempt fallback if sending fails."""
        try:
            self._send_email()
        except (SMTPException, ValidationError) as error:
            logger.error(f"Error sending email to {self.unique_to_emails}: {error}")
            if fallback:
                self._send_fallback_email()
        except Exception as error:
            logger.exception(f"Unexpected error while sending email: {error}")
            if fallback:
                self._send_fallback_email()

        return {
            "is_success": True if len(self.email_sends) else False,
            "successful": self.email_sends,
            "fallback": self.fallback_email_sends,
        }

    def _is_valid_email(self, email: str) -> bool:
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def _get_unique_to_emails(self) -> list[str]:
        processed_emails = []
        for email in self.emails.to_emails:
            valid_email = email if self._is_valid_email(email) else self.from_email
            if valid_email not in processed_emails:
                processed_emails.append(valid_email)
        return processed_emails

    def _validate_templates(self) -> None:
        if not self.templates.text_template.endswith(".txt"):
            raise ValidationError("Text template must end with '.txt'")
        if not self.templates.html_template.endswith(".html"):
            raise ValidationError("HTML template must end with '.html'")
        if self.templates.text_template == self.templates.html_template:
            raise TemplatesError("Text and HTML templates must be different files.")

    def _render_templates(self) -> tuple[str, str]:
        try:
            text_content = render_to_string(self.templates.text_template, self.context)
            html_content = render_to_string(self.templates.html_template, self.context)
            return text_content, html_content
        except Exception as error:
            logger.error(f"Template rendering failed: {error}")
            raise TemplatesError("Template rendering failed.")

    def _send_email(self) -> None:
        text_content, html_content = self._render_templates()

        email = EmailMultiAlternatives(
            subject=self.subject,
            body=text_content,
            from_email=self.from_email,
            to=self.unique_to_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        self.email_sends = self.unique_to_emails
        logger.info(f"Email sent successfully to: {', '.join(self.unique_to_emails)}")

    def _send_fallback_email(self) -> None:
        try:
            text_content, html_content = self._render_templates()

            fallback_email = EmailMultiAlternatives(
                subject=self.subject,
                body=text_content,
                from_email=self.from_email,
                to=[self.from_email],
            )
            fallback_email.attach_alternative(html_content, "text/html")
            fallback_email.send()

            self.fallback_email_sends = [self.from_email]
            logger.info(f"Fallback email sent to: {self.from_email}")
        except Exception as error:
            logger.error(f"Error sending fallback email: {error}")
