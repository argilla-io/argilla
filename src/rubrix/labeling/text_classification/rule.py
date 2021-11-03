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


class Rule:
    """A rule (labeling function) in form of an ElasticSearch query.

    Args:
        query: An ElasticSearch query with the `query string syntax <https://rubrix.readthedocs.io/en/stable/reference/rubrix_webapp_reference.html#search-input>`_.
        label: The label associated to the query.
        name: An optional name for the rule to be used as identifier in the
            `rubrix.labeling.text_classification.WeakLabels` class. By default, we will use the ``query`` string.

    Examples:
        >>> import rubrix as rb
        >>> urgent_rule = Rule(query="inputs.text:(urgent AND immediately)", label="urgent", name="urgent_rule")
        >>> not_urgent_rule = Rule(query="inputs.text:(NOT urgent) AND metadata.title_length>20", label="not urgent")
        >>> not_urgent_rule.apply("my_dataset")
        >>> my_dataset_records = rb.load(name="my_dataset", as_pandas=False)
        >>> not_urgent_rule(my_dataset_records[0])
        "not urgent"
    """

    def __init__(self, query: str, label: str, name: Optional[str] = None):
        self._query = query
        self._label = label
        self._name = name
        self._matching_ids = None

    @property
    def name(self):
        """The name of the rule."""
        if self._name is not None:
            return self._name
        return self._query

    def apply(self, dataset: str):
        """Apply the rule to a dataset and save matching ids of the records.

        Args:
            dataset: The name of the dataset.
        """
        records = rb.load(name=dataset, query=self._query, as_pandas=False)

        self._matching_ids = {record.id: None for record in records}

    def __call__(self, record: TextClassificationRecord) -> Optional[str]:
        """Check if the given record is among the matching ids from the ``self.apply`` call.

        Args:
            record: The record to be labelled.

        Returns:
            A label if the record id is among the matching ids, otherwise None.

        Raises:
            RuleNotAppliedError: If the rule was not applied to the dataset before.
        """
        if self._matching_ids is None:
            raise RuleNotAppliedError(
                "Rule was still not applied. Please call `self.apply(dataset)` first."
            )

        try:
            self._matching_ids[record.id]
        except KeyError:
            return None
        else:
            return self._label


class RuleNotAppliedError(Exception):
    pass
