import asyncio
import random
from typing import Dict, Optional

import wrapt

from rubrix.monitoring.helpers import start_loop_in_thread

_LOGGING_LOOP = None


def _get_current_loop():
    global _LOGGING_LOOP
    if not _LOGGING_LOOP:
        _LOGGING_LOOP = start_loop_in_thread()
    return _LOGGING_LOOP


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

    @property
    def __model__(self):
        """Return the monitored task model"""
        return self.__wrapped__

    def is_record_accepted(self) -> bool:
        """Return True if a record should be logged to rubrix"""
        return random.uniform(0.0, 1.0) <= self.sample_rate

    def _log2rubrix(self, *args, **kwargs):
        raise NotImplementedError()

    def log_async(self, *args, **kwargs):
        wrapped_func = self._log2rubrix
        loop = _get_current_loop()

        async def f():
            return wrapped_func(*args, **kwargs)

        asyncio.run_coroutine_threadsafe(f(), loop)
