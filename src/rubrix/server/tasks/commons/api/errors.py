from typing import Any

from pydantic import PydanticValueError


class MetadataLimitExceededError(PydanticValueError):
    code = "metadata.limit_exceeded"
    msg_template = (
        "Number of keys in metadata ({meta_len}) exceeds the configured limit ({limit})"
    )

    @classmethod
    def new_error(cls, found_len: int, limit: int) -> "MetadataLimitExceededError":
        return cls(meta_len=found_len, limit=limit)
