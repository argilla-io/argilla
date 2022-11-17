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

import atexit
import dataclasses
import logging
import random
import threading
from queue import Empty, Queue
from typing import Any, Dict, Iterable, List, Optional

import backoff
import monotonic
import wrapt

from argilla.client.api import Api
from argilla.client.models import Record
from argilla.client.sdk.commons.errors import ArApiResponseError


class ModelNotSupportedError(Exception):
    pass


class DatasetRecordsConsumer(threading.Thread):
    """Consumes the records from the dataset queue."""

    log = logging.getLogger("argilla.monitoring")

    def __init__(
        self,
        name: str,
        api: Api,
        tags: Optional[dict] = None,
        metadata: Optional[dict] = None,
        buffer_size: int = 10000,
        upload_size=256,
        upload_interval=1.0,
        retries=10,
        timeout=15,
        on_error=None,
    ):
        """Create a consumer thread."""
        threading.Thread.__init__(self)
        self.daemon = True
        self.upload_size = upload_size
        self.upload_interval = upload_interval
        self.api = api
        self.on_error = on_error
        self.queue = Queue(maxsize=buffer_size)
        self.dataset = name
        self.tags = tags
        self.metadata = metadata

        self.running = True
        self.retries = retries
        self.timeout = timeout

    def run(self):
        """Runs the consumer."""
        while self.running:
            self.log_next_batch()

    def pause(self):
        """Pause the consumer."""
        self.running = False

    def log_next_batch(self):
        """Upload the next batch of items, return whether successful."""
        success = False
        batch = self._next_batch()
        if len(batch) == 0:
            return False

        try:
            self._log_records(batch)
            success = True
        except Exception as e:
            self.log.error("error logging data: %s", e)
            success = False
            if self.on_error:
                self.on_error(e, batch)
        finally:
            # mark items as acknowledged from queue
            for _ in batch:
                self.queue.task_done()
            return success

    def _next_batch(self) -> List[Record]:
        queue = self.queue
        records = []

        start_time = monotonic.monotonic()
        while len(records) < self.upload_size:
            elapsed = monotonic.monotonic() - start_time
            if elapsed >= self.upload_interval:
                break
            try:
                item = queue.get(
                    block=True,
                    timeout=self.upload_interval - elapsed,
                )
                records.append(item)
            except Empty:
                break

        return records

    def _log_records(self, batch: List[Record]):
        def fatal_exception(exc):
            if isinstance(exc, ArApiResponseError):
                return (400 <= exc.HTTP_STATUS < 500) and exc.HTTP_STATUS != 429
            else:
                return False

        @backoff.on_exception(
            backoff.expo,
            Exception,
            max_tries=self.retries + 1,
            giveup=fatal_exception,
        )
        def _inner_log_records():
            self.api.log(
                name=self.dataset,
                records=batch,
                tags=self.tags,
                metadata=self.metadata,
                background=True,
                verbose=False,
            )

        _inner_log_records()

    def send(self, records: Iterable[Record]):
        """Send records to the consumer"""
        for record in records:
            self.queue.put(
                item=record,
                block=False,
            )


class BaseMonitor(wrapt.ObjectProxy):
    """
    A base monitor class for easy task model monitoring

    Attributes:
    -----------
    dataset:
        argilla dataset name
    sample_rate:
        The portion of the data to store in argilla. Default = 0.2
    """

    def __init__(
        self,
        *args,
        api: Api,
        dataset: str,
        sample_rate: float = 1.0,
        log_interval: float = 1.0,
        agent: Optional[str] = None,
        tags: Dict[str, str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        assert dataset, "Missing dataset"
        assert (
            0.0 < sample_rate <= 1.0
        ), "Wrong sample rate. Set a value in (0, 1] range."

        self.dataset = dataset
        self.sample_rate = sample_rate
        self.agent = agent
        self.tags = tags
        self._api = api
        self._log_interval = log_interval
        self._consumers: Dict[str, DatasetRecordsConsumer] = {}

        atexit.register(self.shutdown)

    @property
    def __model__(self):
        """Return the monitored task model"""
        return self.__wrapped__

    def is_record_accepted(self) -> bool:
        """Return True if a record should be logged to argilla"""
        return random.uniform(0.0, 1.0) <= self.sample_rate

    def _prepare_log_data(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    def shutdown(self):
        """Stop consumers"""
        for consumer in self._consumers.values():
            try:
                consumer.pause()
                consumer.join()
            except RuntimeError:
                pass

    def send_records(self, *args, **kwargs):
        data = self._prepare_log_data(*args, **kwargs)

        consumer = self._get_consumer_by_dataset(dataset=data["name"])
        consumer.tags = data.get("tags", {})
        consumer.metadata = data.get("metadata", {})
        consumer.send(data["records"])

    def _get_consumer_by_dataset(self, dataset: str):
        if dataset not in self._consumers:
            self._consumers[dataset] = self._create_consumer(dataset)
        return self._consumers[dataset]

    def _create_consumer(self, name: str):
        consumer = DatasetRecordsConsumer(
            name=name,
            api=self._api,
            upload_interval=self._log_interval,
        )
        consumer.start()
        return consumer
