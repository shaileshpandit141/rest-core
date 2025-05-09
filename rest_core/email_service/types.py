from typing import TypedDict


class SendStatusTyped(TypedDict):
    is_success: bool
    successful: list[str]
    fallback: list[str]
