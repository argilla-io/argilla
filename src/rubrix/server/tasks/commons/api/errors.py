from rubrix.server.commons.errors import BadRequestError


class MetadataLimitExceededError(BadRequestError):
    def __init__(self, length: int, limit: int):
        self.len = length
        self.limit = limit
