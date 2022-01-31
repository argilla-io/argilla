class RubrixClientError(Exception):
    pass


class RubrixApiResponseError(RubrixClientError):

    HTTP_STATUS: int

    def __init__(self, **ctx):
        self.ctx = ctx

    def __str__(self):
        return (
            f"Rubrix server returned an error with http status: {self.HTTP_STATUS}"
            + f"\nError details: [{self.ctx}]"
        )


class NotFoundApiError(RubrixApiResponseError):
    HTTP_STATUS = 404


class ValidationApiError(RubrixApiResponseError):
    HTTP_STATUS = 422

    def __init__(self, client_ctx, params, **ctx):

        for error in params.get("errors", []):
            current_level = client_ctx
            for loc in error["loc"]:
                new_value = None
                try:
                    new_value = current_level[loc]
                except KeyError:
                    pass
                if new_value is None:
                    break
                if hasattr(new_value, "dict"):
                    new_value = new_value.dict()
                current_level = new_value
            error["value"] = current_level

        # TODO: parse error details and match with client context
        super().__init__(**ctx, params=params)


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
