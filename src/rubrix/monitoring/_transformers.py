from typing import Any, Dict, List, Tuple

import rubrix
from rubrix import TextClassificationRecord
from rubrix.monitoring.base import BaseMonitor
from rubrix.monitoring.types import MissingType

try:

    from transformers import Pipeline, TextClassificationPipeline
except ModuleNotFoundError:
    TextClassificationPipeline = MissingType
    Pipeline = MissingType


class TextClassificationMonitor(BaseMonitor):
    """Configures monitoring over Hugging Face text classification pipelines"""

    def _log2rubrix(
        self,
        data: List[Tuple[str, Dict[str, Any], List[Any]]],
    ):
        """Register a list of tuples including inputs and its predictions for text classification task"""
        records = []
        config = self.__model__.model.config
        agent = config.name_or_path

        for input_, metadata, predictions in data:
            if isinstance(predictions, dict):
                predictions = [predictions]

            record = TextClassificationRecord(
                inputs=input_,
                prediction=[
                    (prediction["label"], prediction["score"])
                    for prediction in predictions
                ],
                prediction_agent=agent,
                metadata=metadata or {},
            )
            records.append(record)

        rubrix.log(
            records,
            name=self.dataset,
            tags={
                "name": config.name_or_path,
                "transformers_version": config.transformers_version
                or config.to_dict().get("transformers_version"),
                "model_type": config.model_type,
                "task": self.__model__.task,
            },
            metadata=config.to_dict(),
        )

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

            filtered_data = [
                (input_, meta, predictions)
                for input_, meta, predictions in zip(
                    inputs, metadata, batch_predictions
                )
                if self.is_record_accepted()
            ]
            if filtered_data:
                self.log_async(filtered_data)

        finally:
            return batch_predictions


def classifier_monitor(
    pl: TextClassificationPipeline, dataset: str, sample_rate: float
) -> Pipeline:
    return TextClassificationMonitor(pl, dataset=dataset, sample_rate=sample_rate)
