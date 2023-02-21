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

from argilla.client import api
from argilla.metrics import helpers
from argilla.metrics.models import MetricSummary


def text_length(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the input text length metrics for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://argilla.readthedocs.io/en/stable/guides/queries.html)

    Returns:
        The text length metric summary

    Examples:
        >>> from argilla.metrics.commons import text_length
        >>> summary = text_length(name="example-dataset")
        >>> summary.visualize() # will plot an histogram with results
        >>> summary.data # returns the raw result data
    """
    metric = api.active_api().compute_metric(name, metric="text_length", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.histogram(data=metric.results, title=metric.description),
    )


def records_status(name: str, query: Optional[str] = None) -> MetricSummary:
    """Computes the records status distribution for a dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](https://argilla.readthedocs.io/en/stable/guides/queries.html)

    Returns:
        The status distribution  metric summary

    Examples:
        >>> from argilla.metrics.commons import records_status
        >>> summary = records_status(name="example-dataset")
        >>> summary.visualize() # will plot an histogram with results
        >>> summary.data # returns the raw result data
    """
    metric = api.active_api().compute_metric(name, metric="status_distribution", query=query)

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(data=metric.results, title=metric.description),
    )


def keywords(
    name: str,
    query: Optional[str] = None,
    size: int = 20,
) -> MetricSummary:
    """Computes the keywords occurrence distribution in dataset

    Args:
        name:
            The dataset name.
        query:
            An ElasticSearch query with the [query string syntax](
            https://argilla.readthedocs.io/en/stable/guides/queries.html)
        size:
            The number of kewords to retrieve. Default to `20`

    Returns:
        The dataset keywords occurrence distribution

    Examples:
        >>> from argilla.metrics.commons import keywords
        >>> summary = keywords(name="example-dataset")
        >>> summary.visualize() # will plot an histogram with results
        >>> summary.data # returns the raw result data
    """
    assert size > 0, ValueError("size must be greater than 0")
    metric = api.active_api().compute_metric(
        name,
        metric="words_cloud",
        query=query,
        size=size,
    )

    return MetricSummary.new_summary(
        data=metric.results,
        visualization=lambda: helpers.bar(
            data=metric.results,
            title=metric.description,
        ),
    )
