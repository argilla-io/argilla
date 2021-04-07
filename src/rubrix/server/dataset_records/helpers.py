import itertools
from typing import Any, Callable, List, Optional, Type

from fastapi.responses import StreamingResponse
from rubrix.server.commons.models import RecordTaskInfo
from rubrix.server.dataset_records.model import MultiTaskRecord
from rubrix.server.dataset_records.service import DatasetRecordsService


def scan_data_response(
    service: DatasetRecordsService,
    dataset: str,
    owner: Optional[str],
    tasks: List[Type[RecordTaskInfo]],
    chunk_size: int = 1000,
    record_transform: Optional[Callable[[MultiTaskRecord], Any]] = None,
) -> StreamingResponse:
    """Generate an textual stream data response for a dataset scan"""

    async def stream_generator():
        """Converts dataset scan into a text stream"""

        def grouper(n, iterable, fillvalue=None):
            args = [iter(iterable)] * n
            return itertools.zip_longest(fillvalue=fillvalue, *args)

        for batch in grouper(
            n=chunk_size,
            iterable=service.scan_dataset(
                dataset=dataset,
                owner=owner,
                tasks=tasks,
            ),
        ):
            filtered_records = filter(lambda r: r is not None, batch)
            if record_transform:
                filtered_records = map(record_transform, filtered_records)
            yield "\n".join(map(lambda r: r.json(), filtered_records)) + "\n"

    return StreamingResponse(stream_generator(), media_type="application/json")
