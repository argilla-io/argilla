import logging
import warnings
from typing import Any

from ._spacy import Language, ner_monitor
from ._transformers import Pipeline, huggingface_monitor
from .base import ModelNotSupportedError

_LOGGER = logging.getLogger(__name__)


def monitor(task_model: Any, dataset: str, sample_rate: float = 0.3):
    try:
        model_monitor = None
        if isinstance(task_model, Language):
            model_monitor = ner_monitor(
                task_model, dataset=dataset, sample_rate=sample_rate
            )
        elif isinstance(task_model, Pipeline):
            model_monitor = huggingface_monitor(
                task_model, dataset=dataset, sample_rate=sample_rate
            )
        if model_monitor is None:
            raise ModelNotSupportedError()
        return model_monitor
    except ModelNotSupportedError:
        warnings.warn(
            "The provided task model is not supported by monitoring module. "
            "Predictions won't be logged into rubrix"
        )

    return task_model

