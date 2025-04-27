from pydantic import BaseModel


class Emails(BaseModel):
    """Data definition for email addresses."""

    from_email: str | None
    to_emails: list[str]


class Templates(BaseModel):
    """Data definition for email templates."""

    text_template: str
    html_template: str
