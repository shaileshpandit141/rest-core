from typing import Any, TypedDict

# Represents either a single dictionary or a list of dictionaries,
# typically returned by an API.
APIResponseData = dict[str, Any] | list[dict[str, Any]]


# Represents common default validation errors in an API response,
# such as general detail messages or non-field-specific errors.
class DefaultValidationError(TypedDict, total=False):
    detail: str
    non_field_errors: list[str]


# Represents field-specific validation errors in a form or model,
# where each field maps to a list of error messages.
FieldValidationErrors = dict[str, list[str]]


# Represents either default-level or field-level validation errors in an API response.
APIValidationErrors = FieldValidationErrors | DefaultValidationError
