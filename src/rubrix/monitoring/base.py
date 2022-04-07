import asyncio
import random
import threading
from typing import Dict, Optional

import wrapt

from rubrix.client.models import BulkResponse


class ModelNotSupportedError(Exception):
    pass


class BaseMonitor(wrapt.ObjectProxy):
    """
    A base monitor class for easy task model monitoring

    Attributes:
    -----------
    dataset:
        Rubrix dataset name
    sample_rate:
        The portion of the data to store in Rubrix. Default = 0.2
    """

    def __init__(
        self,
        *args,
        dataset: str,
        sample_rate: float,
        agent: Optional[str] = None,
        tags: Dict[str, str] = None,
        **kwargs
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
        self._event_loop, self._event_loop_thread, self._log_future = None, None, None
        self._start_event_loop_if_needed()

    @property
    def __model__(self):
        """Return the monitored task model"""
        return self.__wrapped__

    def is_record_accepted(self) -> bool:
        """Return True if a record should be logged to rubrix"""
        return random.uniform(0.0, 1.0) <= self.sample_rate

    async def _log2rubrix(self, *args, **kwargs) -> BulkResponse:
        raise NotImplementedError()

    def log_async(self, *args, **kwargs):
        self._start_event_loop_if_needed()
        return asyncio.run_coroutine_threadsafe(
            self._log2rubrix(*args, **kwargs), self._event_loop
        )

    def _start_event_loop_if_needed(self):
        """Recreate loop/thread if needed"""
        if self._event_loop is None:
            self._event_loop = asyncio.new_event_loop()
        if self._event_loop_thread is None or not self._event_loop_thread.is_alive():
            self._thread = threading.Thread(
                target=self._event_loop.run_forever, daemon=True
            )
            self._thread.start()
