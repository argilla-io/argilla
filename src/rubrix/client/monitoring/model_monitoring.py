import logging
from typing import Any

from ._spacy import Language, ner_monitor
from ._transformers import TextClassificationPipeline, classifier_monitor

_LOGGER = logging.getLogger(__name__)


def monitoring(task_model: Any, dataset: str, sample_rate: float = 0.3):
    if isinstance(task_model, Language):
        return ner_monitor(task_model, dataset=dataset, sample_rate=sample_rate)
    if isinstance(task_model, TextClassificationPipeline):
        return classifier_monitor(task_model, dataset=dataset, sample_rate=sample_rate)

    _LOGGER.warning(
        "The provided task model is not supported by monitoring module. "
        "Predictions won't be logged into rubrix"
    )
    return task_model
