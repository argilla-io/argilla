from typing import Optional

from fastapi.responses import StreamingResponse
from rubrix.server.tasks.commons.helpers import takeuntil
from smart_open import open as smart_open


def stream_from_uri(uri: str, limit: Optional[int] = None) -> StreamingResponse:
    """
    Stream data file as streaming response

    Parameters
    ----------
    uri:
        The snapshot uri
    limit:
        The number of lines to read. Optional

    Returns
    -------
        An StreamingResponse for uri data streaming

    """

    media_type = "application/json"  # TODO: inferred from uri

    def iterate_uri_content(_uri):
        with smart_open(_uri, "rb") as f:  # TODO: check file encoding
            for line in f:
                yield line

    generator = iterate_uri_content(uri)
    if limit:
        generator = takeuntil(generator, limit=limit)
    return StreamingResponse(generator, media_type=media_type)
