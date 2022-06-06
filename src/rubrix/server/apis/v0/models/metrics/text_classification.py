from typing import Any, ClassVar, Dict, Iterable, List, Optional, Set

from pydantic import Field
from sklearn.metrics import precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer

from rubrix.server.apis.v0.models.metrics.base import (
    BaseMetric,
    PythonMetric,
    TermsAggregation,
)
from rubrix.server.apis.v0.models.metrics.commons import CommonTasksMetrics
from rubrix.server.apis.v0.models.text_classification import TextClassificationRecord


class F1Metric(PythonMetric):
    """
    A basic f1 computation for text classification

    Attributes:
    -----------
        multi_label:
            If True, F1 will be calculated assuming multi class task. Default False
    """

    multi_label: bool = False

    def apply(self, records: Iterable[TextClassificationRecord]) -> Any:
        filtered_records = list(filter(lambda r: r.predicted is not None, records))
        # TODO: This must be precomputed with using a global dataset metric
        ds_labels = {
            label
            for record in filtered_records
            for label in record.annotated_as + record.predicted_as
        }

        if not len(ds_labels):
            return {}

        labels_mapping = {label: i for i, label in enumerate(ds_labels)}
        y_true, y_pred = ([], [])
        for record in filtered_records:
            annotations = record.annotated_as
            predictions = record.predicted_as

            if not self.multi_label:
                y_true.append(labels_mapping[annotations[0]])
                y_pred.append(labels_mapping[predictions[0]])

            else:
                y_true.append([labels_mapping[label] for label in annotations])
                y_pred.append([labels_mapping[label] for label in predictions])

        if self.multi_label:
            mlb = MultiLabelBinarizer(classes=list(labels_mapping.values()))
            y_true = mlb.fit_transform(y_true)
            y_pred = mlb.fit_transform(y_pred)

        micro_p, micro_r, micro_f, _ = precision_recall_fscore_support(
            y_true=y_true, y_pred=y_pred, average="micro"
        )
        macro_p, macro_r, macro_f, _ = precision_recall_fscore_support(
            y_true=y_true, y_pred=y_pred, average="macro"
        )

        per_label = {}
        for label, p, r, f, s in zip(
            labels_mapping.keys(),
            *precision_recall_fscore_support(
                y_true=y_true,
                y_pred=y_pred,
                average=None,
            ),
        ):
            per_label.update(
                {
                    f"{label}_precision": p.tolist(),
                    f"{label}_recall": r.tolist(),
                    f"{label}_f1": f.tolist(),
                    f"{label}_support": s.tolist(),
                }
            )

        return {
            "precision_macro": macro_p,
            "recall_macro": macro_r,
            "f1_macro": macro_f,
            "precision_micro": micro_p,
            "recall_micro": micro_r,
            "f1_micro": micro_f,
            **per_label,
        }


class DatasetLabels(PythonMetric):
    id: str = Field("dataset_labels", const=True)
    name: str = Field("The dataset labels", const=True)
    max_processed_records: int = 10000

    def apply(self, records: Iterable[TextClassificationRecord]) -> Dict[str, Any]:
        ds_labels = set()
        for _ in range(
            0, self.max_processed_records
        ):  # Only a few of records will be parsed
            record = next(records, None)
            if record is None:
                break

            if record.annotation:
                ds_labels.update(
                    [label.class_label for label in record.annotation.labels]
                )
            if record.prediction:
                ds_labels.update(
                    [label.class_label for label in record.prediction.labels]
                )
        return {"labels": ds_labels or []}


class TextClassificationMetrics(CommonTasksMetrics[TextClassificationRecord]):
    """Configured metrics for text classification task"""

    metrics: ClassVar[List[BaseMetric]] = CommonTasksMetrics.metrics + [
        TermsAggregation(
            id="predicted_as",
            name="Predicted labels distribution",
            field="predicted_as",
        ),
        TermsAggregation(
            id="annotated_as",
            name="Annotated labels distribution",
            field="annotated_as",
        ),
        F1Metric(
            id="F1",
            name="F1 Metrics for single-label",
            description="F1 Metrics for single-label (averaged and per label)",
        ),
        F1Metric(
            id="MultiLabelF1",
            name="F1 Metrics for multi-label",
            description="F1 Metrics for multi-label (averaged and per label)",
            multi_label=True,
        ),
        DatasetLabels(),
    ]
