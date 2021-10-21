from typing import Any, ClassVar, List

import pandas as pd

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

    def apply(self, query_df: pd.DataFrame) -> Any:
        from sklearn.metrics import f1_score
        from sklearn.preprocessing import MultiLabelBinarizer

        if not (
            "predicted_as" in query_df.columns and "annotated_as" in query_df.columns
        ):
            return {}

        df = query_df[["predicted_as", "annotated_as"]].dropna()
        df = df[
            df.apply(
                lambda d: len(d["predicted_as"]) > 0 and len(d["annotated_as"]) > 0,
                axis=1,
            )
        ]

        ds_labels = set()
        df.predicted_as.map(lambda labels: [ds_labels.add(l) for l in labels])
        df.annotated_as.map(lambda labels: [ds_labels.add(l) for l in labels])

        labels_mapping = {label: i for i, label in enumerate(ds_labels)}
        if not labels_mapping:
            return {}

        y_true, y_pred = ([], [])
        for array, column in [(y_true, "annotated_as"), (y_pred, "predicted_as")]:
            array.extend(
                df[column]
                .map(
                    lambda x: labels_mapping[x[0]]
                    if not self.multi_label
                    else [labels_mapping[l] for l in x]
                )
                .values
            )
        if self.multi_label:
            mlb = MultiLabelBinarizer(list(labels_mapping.values()))
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

        return {"micro": micro, "macro": macro, **per_label}


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
