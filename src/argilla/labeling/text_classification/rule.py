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
from typing import Dict, List, Optional, Union

import argilla as rg
from argilla import TextClassificationRecord
from argilla.client import api
from argilla.client.sdk.text_classification.models import LabelingRule


class Rule:
    """A rule (labeling function) in form of an ElasticSearch query.

    Args:
        query: An ElasticSearch query with the `query string syntax <https://argilla.readthedocs.io/en/stable/guides/queries.html>`_.
        label: The label associated to the query. Can also be a list of labels.
        name: An optional name for the rule to be used as identifier in the
            `argilla.labeling.text_classification.WeakLabels` class. By default, we will use the ``query`` string.

    Examples:
        >>> import argilla as rg
        >>> urgent_rule = Rule(query="inputs.text:(urgent AND immediately)", label="urgent", name="urgent_rule")
        >>> not_urgent_rule = Rule(query="inputs.text:(NOT urgent) AND metadata.title_length>20", label="not urgent")
        >>> not_urgent_rule.apply("my_dataset")
        >>> my_dataset_records = rg.load(name="my_dataset")
        >>> not_urgent_rule(my_dataset_records[0])
        "not urgent"
    """

    def __init__(
        self,
        query: str,
        label: Union[str, List[str]],
        name: Optional[str] = None,
        author: Optional[str] = None,
    ):
        self._query = query
        self._label = label
        self._name = name
        self._author = author
        self._matching_ids = None

    @property
    def query(self) -> str:
        """The rule query"""
        return self._query

    @property
    def label(self) -> Union[str, List[str]]:
        """The rule label"""
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def name(self):
        """The name of the rule."""
        if self._name is not None:
            return self._name
        return self._query

    @property
    def author(self):
        """Who authored the rule."""
        return self._author

    def _convert_to_labeling_rule(self):
        """Converts the rule to a LabelingRule"""
        if isinstance(self._label, str):
            labels = [self._label]
        else:
            labels = self._label

        return LabelingRule(query=self.query, labels=labels)

    def add_to_dataset(self, dataset: str):
        """Add to rule to the given dataset"""
        api.active_api().add_dataset_labeling_rules(dataset, rules=[self._convert_to_labeling_rule()])

    def remove_from_dataset(self, dataset: str):
        """Removes the rule from the given dataset"""

        api.active_api().delete_dataset_labeling_rules(dataset, rules=[self._convert_to_labeling_rule()])

    def update_at_dataset(self, dataset: str):
        """Updates the rule at the given dataset"""
        api.active_api().update_dataset_labeling_rules(dataset, rules=[self._convert_to_labeling_rule()])

    def apply(self, dataset: str):
        """Apply the rule to a dataset and save matching ids of the records.

        Args:
            dataset: The name of the dataset.
        """
        records = rg.load(name=dataset, query=self._query)

        self._matching_ids = {record.id: None for record in records}

    def metrics(self, dataset: str) -> Dict[str, Union[int, float]]:
        """Compute the rule metrics for a given dataset:

        - **coverage**: Fraction of the records labeled by the rule.
        - **annotated_coverage**: Fraction of annotated records labeled by the rule.
        - **correct**: Number of records the rule labeled correctly (if annotations are available).
        - **incorrect**: Number of records the rule labeled incorrectly (if annotations are available).
        - **precision**: Fraction of correct labels given by the rule (if annotations are available). The precision does not penalize the rule for abstains.

        Args:
            dataset: Name of the dataset for which to compute the rule metrics.

        Returns:
            The rule metrics.
        """
        metrics = api.active_api().rule_metrics_for_dataset(
            dataset=dataset,
            rule=LabelingRule(query=self.query, label=self.label),
        )

        return {
            "coverage": metrics.coverage,
            "annotated_coverage": metrics.coverage_annotated,
            "correct": int(metrics.correct) if metrics.correct is not None else None,
            "incorrect": int(metrics.incorrect) if metrics.incorrect is not None else None,
            "precision": metrics.precision if metrics.precision is not None else None,
        }

    def __call__(self, record: TextClassificationRecord) -> Optional[Union[str, List[str]]]:
        """Check if the given record is among the matching ids from the ``self.apply`` call.

        Args:
            record: The record to be labelled.

        Returns:
            A label or list of labels if the record id is among the matching ids, otherwise None.

        Raises:
            RuleNotAppliedError: If the rule was not applied to the dataset before.
        """
        if self._matching_ids is None:
            raise RuleNotAppliedError("Rule was still not applied. Please call `self.apply(dataset)` first.")

        try:
            self._matching_ids[record.id]
        except KeyError:
            return None
        else:
            return self._label

    def __repr__(self):
        """The rule representation."""
        return f"Rule(query='{self.query}', label='{self.label}', name='{self.name}')"

    def __str__(self):
        """The rule string representation."""
        return repr(self)


def add_rules(dataset: str, rules: List[Rule]):
    """Adds the rules to a given dataset

    Args:
        dataset: Name of the dataset.
        rules: Rules to add to the dataset

    Returns:
    """
    rules = [rule._convert_to_labeling_rule() for rule in rules]
    return api.active_api().add_dataset_labeling_rules(dataset, rules)


def delete_rules(dataset: str, rules: List[Rule]):
    """Deletes the rules from the given dataset

    Args:
        dataset: Name of the dataset
        rules: Rules to delete from the dataset

    Returns:
    """
    rules = [rule._convert_to_labeling_rule() for rule in rules]
    api.active_api().delete_dataset_labeling_rules(dataset, rules)


def update_rules(dataset: str, rules: List[Rule]):
    """Updates the rules of the given dataset

    Args:
        dataset: Name of the dataset
        rules: Rules to update at the dataset

    Returns:
    """
    rules = [rule._convert_to_labeling_rule() for rule in rules]
    api.active_api().update_dataset_labeling_rules(dataset, rules)


def load_rules(dataset: str) -> List[Rule]:
    """load the rules defined in a given dataset.

    Args:
        dataset: Name of the dataset.

    Returns:
        A list of rules defined in the given dataset.
    """
    rules = api.active_api().fetch_dataset_labeling_rules(dataset)
    return [
        Rule(
            query=rule.query,
            label=rule.label or rule.labels,
            name=rule.description,
            author=rule.author,
        )
        for rule in rules
    ]


class RuleNotAppliedError(Exception):
    pass
