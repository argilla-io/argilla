#  coding=utf-8
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

import rubrix as rb
from rubrix import TextClassificationRecord
from rubrix.client import _check_response_errors
from rubrix.client.sdk.text_classification.api import data
from rubrix.client.sdk.text_classification.models import TextClassificationQuery


class Rule:
    """A rule (labeling function) in form of an ElasticSearch query

    Args:
        query: A ElasticSearch query with the [query string syntax](https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input)
        label: The label associated to the query
    """

    def __init__(self, query: str, label: str):
        self._query: TextClassificationQuery = TextClassificationQuery(
            query_inputs=query
        )
        self._label = label
        self._matching_ids = None

    @classmethod
    def load(cls):
        """Load a rule defined in the Rubrix web app."""
        raise NotImplementedError

    def apply(self, dataset: str):
        """Apply the rule to a dataset and save matching ids of the records.

        Args:
            dataset: The name of the dataset
        """
        client = rb._client_instance()._client
        response = data(client=client, name=dataset, request=self._query)
        _check_response_errors(response)

        self._matching_ids = [record.id for record in response.parsed]

    def __call__(self, record: TextClassificationRecord) -> Optional[str]:
        if self._matching_ids is None:
            raise RuleNotAppliedError(
                "Rule was still not applied. Please call `self.apply(dataset)` first"
            )

        if record.id in self._matching_ids:
            return self._label


class RuleNotAppliedError(Exception):
    pass
