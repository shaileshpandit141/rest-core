import logging
from .builder import EmailBuilder
from .strategies import NormalSendStrategy, FallbackSendStrategy

logger = logging.getLogger(__name__)


class SendEmailService:
    def __init__(self, builder: EmailBuilder) -> None:
        self.builder = builder
        self.normal_strategy = NormalSendStrategy()
        self.fallback_strategy = FallbackSendStrategy()

    def send(self) -> None:
        data = self.builder.build().get_data()
        try:
            self.normal_strategy.send(
                subject=data["subject"],
                body=data["text_body"],
                html_body=data["html_body"],
                from_email=data["from_email"],
                to_emails=data["to_emails"],
            )
            logger.info(f"Email successfully sent to {data['to_emails']}")
        except Exception as e:
            logger.error(f"Normal send failed: {e}")
            self._send_fallback(data)

    def _send_fallback(self, data) -> None:
        try:
            self.fallback_strategy.send(
                subject=data["subject"],
                body=data["text_body"],
                html_body=data["html_body"],
                from_email=data["from_email"],
                to_emails=[data["from_email"]],
            )
            logger.info(f"Fallback email sent to {data['from_email']}")
        except Exception as e:
            logger.critical(f"Fallback send also failed: {e}")
