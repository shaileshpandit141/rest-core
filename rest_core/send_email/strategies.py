from abc import ABC, abstractmethod
from django.core.mail import EmailMultiAlternatives
from typing import List


class SendStrategy(ABC):
    @abstractmethod
    def send(
        self,
        subject: str,
        body: str,
        html_body: str,
        from_email: str,
        to_emails: List[str],
    ) -> None:
        pass


class NormalSendStrategy(SendStrategy):
    def send(self, subject, body, html_body, from_email, to_emails) -> None:
        email = EmailMultiAlternatives(subject, body, from_email, to_emails)
        email.attach_alternative(html_body, "text/html")
        email.send()


class FallbackSendStrategy(SendStrategy):
    def send(self, subject, body, html_body, from_email, to_emails) -> None:
        email = EmailMultiAlternatives(subject, body, from_email, [from_email])
        email.attach_alternative(html_body, "text/html")
        email.send()
