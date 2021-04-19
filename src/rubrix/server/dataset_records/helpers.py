import itertools
from typing import Any, Callable, List, Optional, Type, Union

from fastapi.responses import StreamingResponse
from rubrix.server.commons.models import RecordTaskInfo
from rubrix.server.dataset_records.model import MultiTaskRecord
from rubrix.server.dataset_records.service import DatasetRecordsService


def takeuntil(iterable, limit: int):
    """
    Iterate over inner iterable until a count limit

    Parameters
    ----------
    iterable:
        The inner iterable
    limit:
        The limit

    Returns
    -------

    """
    count = 0
    for e in iterable:
        if count < limit:
            yield e
            count += 1
        else:
            break


def scan_data_response(
    service: DatasetRecordsService,
    dataset: str,
    owner: Optional[str],
    tasks: List[Type[RecordTaskInfo]],
    chunk_size: int = 1000,
    limit: Optional[int] = None,
    ids: Optional[List[Union[str, int]]] = None,
    record_transform: Optional[Callable[[MultiTaskRecord], Any]] = None,
) -> StreamingResponse:
    """Generate an textual stream data response for a dataset scan"""

    async def stream_generator():
        """Converts dataset scan into a text stream"""

        def grouper(n, iterable, fillvalue=None):
            args = [iter(iterable)] * n
            return itertools.zip_longest(fillvalue=fillvalue, *args)

        data_stream = service.read_dataset(
            dataset=dataset,
            owner=owner,
            tasks=tasks,
            ids=ids,
        )
        if limit:
            data_stream = takeuntil(data_stream, limit=limit)

        for batch in grouper(
            n=chunk_size,
            iterable=data_stream,
        ):
            filtered_records = filter(lambda r: r is not None, batch)
            if record_transform:
                filtered_records = map(record_transform, filtered_records)
            yield "\n".join(map(lambda r: r.json(by_alias=True), filtered_records)) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/json")
