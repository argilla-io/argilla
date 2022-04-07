#  coding=utf-8
#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import asyncio
import logging
import threading
from typing import Any, Dict, Iterable, Optional, Union

from rubrix.client.api import Api
from rubrix.client.datasets import Dataset
from rubrix.client.models import BulkResponse, Record
from rubrix.client.sdk.commons.api import async_bulk

_LOGGER = logging.getLogger(__name__)


class AsyncApi(Api):
    """This API class substitutes some of its methods with asyncio compatible coroutines.

    It also provides some convenient methods to quickly set up an event loop in a secondary thread.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._event_loop = None
        self._thread = None

    @property
    def event_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """The event loop."""
        return self._event_loop

    @property
    def thread(self) -> Optional[asyncio.AbstractEventLoop]:
        """The thread where the event loop runs."""
        return self._thread

    def _setup_loop_in_thread(self):
        """Setups the eventloop in a new thread.

        This does nothing, if the eventloop is already running in its own thread.
        Otherwise, it will create/start an eventloop in a newly created Thread.
        """
        if self._event_loop is None:
            self._event_loop = asyncio.new_event_loop()
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(
                target=self._event_loop.run_forever, daemon=True
            )
            self._thread.start()

    def future_log(self, *args, **kwargs) -> asyncio.Future:
        """Logs records to Rubrix in another thread with asyncio.

        This is useful if you want to asynchronously log records to Rubrix and do not care about the eventloop.

        Args:
            *args/**kwargs: Passed on to ``self.log``

        Returns:
            The future response of the log call.

        Example:
        """
        self._setup_loop_in_thread()
        future_response = asyncio.run_coroutine_threadsafe(
            self.log(*args, **kwargs), self._loop
        )

        return future_response

    async def log(
        self,
        records: Union[Record, Iterable[Record], Dataset],
        name: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 500,
    ) -> BulkResponse:
        """Logs Records to Rubrix with asyncio.

        Args:
            records: The record, an iterable of records, or a dataset to log.
            name: The dataset name.
            tags: A dictionary of tags related to the dataset.
            metadata: A dictionary of extra info for the dataset.
            chunk_size: The chunk size for a data bulk.

        Returns:
            Summary of the response from the REST API
        """
        tags = tags or {}
        metadata = metadata or {}

        bulk_class, creation_class = self._log(
            records=records, name=name, chunk_size=chunk_size
        )

        processed, failed = 0, 0
        for i in range(0, len(records), chunk_size):
            chunk = records[i : i + chunk_size]

            response = await async_bulk(
                client=self._client,
                name=name,
                json_body=bulk_class(
                    tags=tags,
                    metadata=metadata,
                    records=[creation_class.from_client(r) for r in chunk],
                ),
            )

            processed += response.parsed.processed
            failed += response.parsed.failed

        # Creating a composite BulkResponse with the total processed and failed
        return BulkResponse(dataset=name, processed=processed, failed=failed)
