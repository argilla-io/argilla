import asyncio
import random

import wrapt

from rubrix.monitoring.helpers import start_loop_in_thread

_LOGGING_LOOP = None


def _get_current_loop():
    global _LOGGING_LOOP
    if not _LOGGING_LOOP:
        _LOGGING_LOOP = start_loop_in_thread()
    return _LOGGING_LOOP


class BaseMonitor(wrapt.ObjectProxy):
    """
    A base monitor class for easy task model monitoring

    Attributes:
    -----------

    dataset:
        Rubrix dataset name

    sample_rate:
        Portion or data to store in rubrix. Default = 0.2

    """

    def __init__(self, *args, dataset: str, sample_rate: float, **kwargs):
        super().__init__(*args, **kwargs)

        assert dataset, "Missing dataset"
        assert (
            0.0 < sample_rate <= 1.0
        ), "Wrong sample rate. Set a value in (0, 1] range."

        self.dataset = dataset
        self.sample_rate = sample_rate

    @property
    def __model__(self):
        """Return the monitored task model"""
        return self.__wrapped__

    def is_record_accepted(self) -> bool:
        """Return True if a record should be logged to rubrix"""
        return random.uniform(0.0, 1.0) <= self.sample_rate

    def run_separate(self, coroutine):
        loop = _get_current_loop()
        asyncio.run_coroutine_threadsafe(coroutine, loop)
