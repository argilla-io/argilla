class RubrixClientError(Exception):
    pass


class RubrixApiResponseError(RubrixClientError):

    HTTP_STATUS: int

    def __init__(self, **ctx):
        self.ctx = ctx

    def __str__(self):
        return (
            f"Rubrix server returned an error with http status: {self.HTTP_STATUS}"
            f"\nError details: [{self.ctx}]"
        )


class NotFoundApiError(RubrixApiResponseError):
    HTTP_STATUS = 404


class ValidationApiError(RubrixApiResponseError):
    HTTP_STATUS = 422
    # TODO: Here we can process response and make human readable


class BadRequestApiError(RubrixApiResponseError):
    HTTP_STATUS = 400


class UnauthorizedApiError(RubrixApiResponseError):
    HTTP_STATUS = 401


class ForbiddenApiError(RubrixApiResponseError):
    HTTP_STATUS = 403


class AlreadyExistsApiError(RubrixApiResponseError):
    HTTP_STATUS = 409


class GenericApiError(RubrixApiResponseError):
    HTTP_STATUS = 500
