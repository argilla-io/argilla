from typing import Any, ClassVar, Dict, Iterable, List

from sklearn.metrics import f1_score
from sklearn.preprocessing import MultiLabelBinarizer

from rubrix.server.tasks.commons.metrics.model.base import (
    BaseMetric,
    BaseTaskMetrics,
    PythonMetric,
)
from rubrix.server.tasks.text_classification import TextClassificationRecord


class F1Metric(PythonMetric):
    """
    A basic f1 calculation for text classification

    Attributes:
    -----------
        multi_label:
            If True, F1 will be calculated assuming multi class task. Default False
    """

    multi_label: bool = False

    def apply(self, records: Iterable[Dict[str, Any]]) -> Any:
        filtered_records = filter(
            lambda r: all(
                [
                    len(r.get(field, [])) > 0
                    for field in ["predicted_as", "annotated_as"]
                ]
            ),
            records,
        )

        filtered_records = list(filtered_records)
        ds_labels = set()
        # TODO: This must be precalculated with using a global dataset metric
        for record in filtered_records:
            for label in record["predicted_as"] + record["annotated_as"]:
                ds_labels.add(label)

        if not len(ds_labels):
            return {}

        labels_mapping = {label: i for i, label in enumerate(ds_labels)}
        y_true, y_pred = ([], [])
        for record in filtered_records:
            annotations = record["annotated_as"]
            predictions = record["predicted_as"]

            if not self.multi_label:
                annotations = annotations[:1]
                predictions = predictions[:1]

            y_true.extend([labels_mapping[label] for label in annotations])
            y_pred.extend([labels_mapping[label] for label in predictions])

        if self.multi_label:
            mlb = MultiLabelBinarizer(classes=list(labels_mapping.values()))
            y_true = mlb.fit_transform(y_true)
            y_pred = mlb.fit_transform(y_pred)

        micro = f1_score(y_true=y_true, y_pred=y_pred, average="micro")
        macro = f1_score(y_true=y_true, y_pred=y_pred, average="macro")

        reverse_labels_mapping = {v: k for k, v in labels_mapping.items()}
        per_label = {
            reverse_labels_mapping[i]: f1score
            for i, f1score in enumerate(
                f1_score(
                    y_true=y_true,
                    y_pred=y_pred,
                    labels=list(labels_mapping.values()),
                    average=None,
                )
            )
        }

        return {"micro": micro, "macro": macro,  "per_label": per_label}


class TextClassificationMetrics(BaseTaskMetrics[TextClassificationRecord]):
    """Configured metrics for text classification task"""

    metrics: ClassVar[List[BaseMetric]] = [
        F1Metric(id="F1", name="F1 Metric for single class", description=""),
        F1Metric(
            id="MultiLabelF1",
            name="F1 Metric for multi-class task",
            description="",
            multi_label=True,
        ),
    ]
