from typing import Any, Callable


class EmailServiceValidator:
    def validate(
        self,
        data: Any,
        excepted_data_class: Any,
        exception_class: Callable,
        message: str,
    ) -> None:
        if not isinstance(data, excepted_data_class):
            raise exception_class(message)
