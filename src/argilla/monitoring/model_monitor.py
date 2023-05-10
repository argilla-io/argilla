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

import logging
import warnings
from typing import Optional, Union

from ..client.api import active_api
from ._flair import SequenceTagger, flair_monitor
from ._spacy import Language, ner_monitor
from ._transformers import Pipeline, huggingface_monitor
from .base import BaseMonitor

_LOGGER = logging.getLogger(__name__)


def monitor(
    task_model: Union[Language, Pipeline, SequenceTagger],
    dataset: str,
    sample_rate: float = 0.3,
    agent: Optional[str] = None,
    log_interval: float = 5,
) -> Union[BaseMonitor, Language, Pipeline, SequenceTagger]:
    """Automatically monitor (i.e. log) data fed through Transformer pipelines,
    spaCy models or flAIr taggers.

    Args:
        task_model (Union[Language, Pipeline, SequenceTagger]): The spaCy `Language`,
            transformers `Pipeline` or flAIr `SequenceTagger`.
        dataset (str): The Argilla dataset to log data into.
        sample_rate (float, optional): The portion of processed data to log. Defaults to 0.3.
        agent (Optional[str], optional): The name of the logging agent. Defaults to None.
        log_interval (float, optional): The interval for uploading in seconds. Defaults to 5.

    Returns:
        Union[BaseMonitor, Language, Pipeline, SequenceTagger]: The monitor that acts equivalently
            to the input task_model.
    """
    model_monitor = None
    api = active_api()
    if isinstance(task_model, Language):
        model_monitor = ner_monitor(
            task_model,
            api=api,
            dataset=dataset,
            sample_rate=sample_rate,
            log_interval=log_interval,
        )
    elif isinstance(task_model, Pipeline):
        model_monitor = huggingface_monitor(
            task_model,
            api=api,
            dataset=dataset,
            sample_rate=sample_rate,
            log_interval=log_interval,
        )
    elif isinstance(task_model, SequenceTagger):
        model_monitor = flair_monitor(
            task_model,
            api=api,
            dataset=dataset,
            sample_rate=sample_rate,
            log_interval=log_interval,
        )
    if model_monitor:
        model_monitor.agent = agent
        return model_monitor

    warnings.warn(
        "The provided task model is not supported by monitoring module. Predictions won't be logged into argilla."
    )
    return task_model
