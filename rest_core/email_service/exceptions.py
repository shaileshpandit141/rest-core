class EmailsError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TemplatesError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
