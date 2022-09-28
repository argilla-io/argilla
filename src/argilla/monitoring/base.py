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
import random
import threading
from typing import Any, Dict, Optional

import wrapt

import argilla


class ModelNotSupportedError(Exception):
    pass


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
        """Return True if a record should be logged to argilla"""
        return random.uniform(0.0, 1.0) <= self.sample_rate

    def _prepare_log_data(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError()

    def log_async(self, *args, **kwargs):
        log_args = self._prepare_log_data(*args, **kwargs)
        log_args.pop("verbose", None)
        log_args.pop("background", None)
        return argilla.log(**log_args, verbose=False, background=True)

    def _start_event_loop_if_needed(self):
        """Recreate loop/thread if needed"""
        if self._event_loop is None:
            self._event_loop = asyncio.new_event_loop()
        if self._event_loop_thread is None or not self._event_loop_thread.is_alive():
            self._thread = threading.Thread(
                target=self._event_loop.run_forever, daemon=True
            )
            self._thread.start()
