from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

import rubrix as rb
from rubrix import TextClassificationRecord
from rubrix.client.models import BulkResponse
from rubrix.monitoring.base import BaseMonitor
from rubrix.monitoring.types import MissingType

try:
    from transformers import (
        Pipeline,
        TextClassificationPipeline,
        ZeroShotClassificationPipeline,
    )
    from transformers import __version__ as _transformers_version
except ModuleNotFoundError:
    TextClassificationPipeline = MissingType
    Pipeline = MissingType
    ZeroShotClassificationPipeline = MissingType
    _transformers_version = None


class LabelPrediction(BaseModel):
    label: str
    score: float


class HuggingFaceMonitor(BaseMonitor):
    @staticmethod
    def fetch_transformers_version(config) -> Optional[str]:
        config_dict = config.to_dict()
        return config_dict.get("transformers_version", _transformers_version)

    @property
    def model_config(self):
        return self.__model__.model.config

    def _prepare_log_data(
        self,
        data: List[Tuple[str, Dict[str, Any], List[LabelPrediction]]],
        multi_label: bool = False,
    ) -> Dict[str, Any]:

        agent = self.model_config.name_or_path

        records = []
        for input_, metadata, predictions in data:
            record = TextClassificationRecord(
                text=input_ if isinstance(input_, str) else None,
                inputs=input_ if not isinstance(input_, str) else None,
                prediction=[
                    (prediction.label, prediction.score) for prediction in predictions
                ],
                prediction_agent=agent,
                metadata=metadata or {},
                multi_label=multi_label,
                event_timestamp=datetime.utcnow(),
            )
            records.append(record)

        dataset_name = self.dataset
        if multi_label:
            dataset_name += "_multi"

        return dict(
            records=records,
            name=dataset_name,
            tags={
                "name": self.model_config.name_or_path,
                "transformers_version": self.fetch_transformers_version(
                    self.model_config
                ),
                "model_type": self.model_config.model_type,
                "task": self.__model__.task,
            },
            metadata=self.model_config.to_dict(),
            verbose=False,
        )


class ZeroShotMonitor(HuggingFaceMonitor):
    def __call__(
        self,
        sequences: Union[str, List[str]],
        candidate_labels: List[str],
        *args,
        **kwargs
    ):
        metadata = (kwargs.pop("metadata", None) or {}).copy()
        hypothesis_template = kwargs.get("hypothesis_template", "@default")
        multi_label = kwargs.get("multi_label", kwargs.get("multi_class", False))
        batch_predictions = self.__model__(sequences, candidate_labels, *args, **kwargs)
        try:
            if not isinstance(sequences, list):
                sequences = [sequences]

            predictions = batch_predictions
            if not isinstance(batch_predictions, list):
                predictions = [batch_predictions]

            predictions = [
                [
                    LabelPrediction(label=label, score=score)
                    for label, score in zip(prediction["labels"], prediction["scores"])
                ]
                for prediction in predictions
            ]

            if not metadata:
                metadata = [{}] * len(sequences)
            elif not isinstance(metadata, list):
                metadata = [metadata]
            for meta in metadata:
                meta.update(
                    {
                        "labels": candidate_labels,
                        "hypothesis_template": hypothesis_template,
                    }
                )
            filtered_data = [
                (input_, meta, predictions_)
                for input_, meta, predictions_ in zip(sequences, metadata, predictions)
                if self.is_record_accepted()
            ]
            if filtered_data:
                self.log_async(filtered_data, multi_label=multi_label)

        finally:
            return batch_predictions


class TextClassificationMonitor(HuggingFaceMonitor):
    """Configures monitoring over Hugging Face text classification pipelines"""

    def __call__(self, inputs, *args, **kwargs):
        metadata = kwargs.pop("metadata", None)
        batch_predictions = self.__model__(inputs, *args, **kwargs)
        try:
            if not isinstance(inputs, list):
                inputs = [inputs]
            if not metadata:
                metadata = [None] * len(inputs)
            elif not isinstance(metadata, list):
                metadata = [metadata]

            predictions_ = []
            for pred in batch_predictions:
                if isinstance(pred, dict):
                    pred = [pred]
                predictions_.append([LabelPrediction.parse_obj(p) for p in pred])

            filtered_data = [
                (input_, meta, predictions)
                for input_, meta, predictions in zip(inputs, metadata, predictions_)
                if self.is_record_accepted()
            ]
            if filtered_data:
                self.log_async(filtered_data)

        finally:
            return batch_predictions


def huggingface_monitor(
    pl: Pipeline, dataset: str, sample_rate: float
) -> Optional[Pipeline]:
    if isinstance(pl, TextClassificationPipeline):
        return TextClassificationMonitor(pl, dataset=dataset, sample_rate=sample_rate)
    if isinstance(pl, ZeroShotClassificationPipeline):
        return ZeroShotMonitor(pl, dataset=dataset, sample_rate=sample_rate)
    return None
