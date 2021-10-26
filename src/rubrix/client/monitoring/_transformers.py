from typing import Any, Dict, List, Tuple

import rubrix

from rubrix import TextClassificationRecord
from rubrix.client.monitoring.base import BaseMonitor

try:

    from transformers import Pipeline, TextClassificationPipeline
except ModuleNotFoundError:
    pass


class _TextClassificationMonitor(BaseMonitor):
    """Configures monitoring over Hugging Face text classification pipelines"""

    async def __log_to_rubrix__(
        self,
        data: List[Tuple[str, Dict[str, Any], List[Any]]],
    ):
        """Register a list of tuples including inputs and its predictions for text classification task"""
        records = []
        for input_, metadata, predictions in data:
            if isinstance(predictions, dict):
                predictions = [predictions]

            agent = self.model.model.__class__.__name__
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

        rubrix.log(records, name=self.dataset, tags={"task": self.model.task})

    def __call__(self, inputs, *args, **kwargs):
        metadata = kwargs.pop("metadata", None)
        batch_predictions = self.model(inputs, *args, **kwargs)
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
                self.run_separate(self.__log_to_rubrix__(filtered_data))

        finally:
            return batch_predictions


def classifier_monitor(pl: Pipeline, dataset: str, sample_rate: float) -> Pipeline:
    assert isinstance(pl, TextClassificationPipeline)
    return _TextClassificationMonitor(pl, dataset=dataset, sample_rate=sample_rate)
