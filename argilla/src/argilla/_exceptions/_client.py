from argilla._exceptions._base import ArgillaError

class ArgillaCredentialsError(ArgillaError):
    def __init__(self, message: str = "Credentials are missing or invalid") -> None:
        super().__init__(message)
