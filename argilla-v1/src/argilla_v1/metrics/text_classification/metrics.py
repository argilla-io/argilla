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

from typing import Optional

from argilla_v1.client import singleton
from argilla_v1.metrics import helpers
from argilla_v1.metrics.models import MetricSummary


def f1(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the single label f1 metric for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html)

    Returns:
        The f1 metric summary

    Examples:
        >>> from argilla_v1.metrics.text_classification import f1
        >>> summary = f1(name="example-dataset")
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # returns the raw result data
    """
    metric = singleton.active_api().compute_metric(name, metric="F1", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.f1(data=metric.results, title=metric.description),
    )


def f1_multilabel(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the multi-label label f1 metric for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://docs.v1.argilla.io/en/latest/practical_guides/filter_dataset.html)

    Returns:
        The f1 metric summary

    Examples:
        >>> from argilla_v1.metrics.text_classification import f1_multilabel
        >>> summary = f1_multilabel(name="example-dataset")
        >>> summary.visualize() # will plot a bar chart with results
        >>> summary.data # returns the raw result data
    """
    metric = singleton.active_api().compute_metric(name, metric="MultiLabelF1", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.f1(data=metric.results, title=metric.description),
    )
