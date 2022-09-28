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

from typing import List, Optional, Tuple

from fastapi import Depends
from pydantic import BaseModel, Field

from argilla.server.daos.datasets import DatasetsDAO
from argilla.server.daos.models.records import DaoRecordsSearch
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.errors import EntityAlreadyExistsError, EntityNotFoundError
from argilla.server.services.search.model import ServiceBaseRecordsQuery
from argilla.server.services.tasks.text_classification.model import (
    ServiceLabelingRule,
    ServiceTextClassificationDataset,
)


class DatasetLabelingRulesSummary(BaseModel):
    covered_records: int
    annotated_covered_records: int


class LabelingRuleSummary(BaseModel):
    covered_records: int
    annotated_covered_records: int
    correct_records: int = Field(default=0)
    incorrect_records: int = Field(default=0)
    precision: Optional[float] = None


class LabelingService:

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        datasets: DatasetsDAO = Depends(DatasetsDAO.get_instance),
        records: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
    ):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(datasets, records)
        return cls._INSTANCE

    def __init__(self, datasets: DatasetsDAO, records: DatasetRecordsDAO):
        self.__datasets__ = datasets
        self.__records__ = records

    # TODO(@frascuchon): Move all rules management methods to the common datasets service like settings
    def list_rules(
        self, dataset: ServiceTextClassificationDataset
    ) -> List[ServiceLabelingRule]:
        """List a set of rules for a given dataset"""
        return dataset.rules

    def delete_rule(self, dataset: ServiceTextClassificationDataset, rule_query: str):
        """Delete a rule from a dataset by its defined query string"""
        new_rules_set = [r for r in dataset.rules if r.query != rule_query]
        if len(dataset.rules) != new_rules_set:
            dataset.rules = new_rules_set
            self.__datasets__.update_dataset(dataset)

    def add_rule(
        self, dataset: ServiceTextClassificationDataset, rule: ServiceLabelingRule
    ) -> ServiceLabelingRule:
        """Adds a rule to a dataset"""
        for r in dataset.rules:
            if r.query == rule.query:
                raise EntityAlreadyExistsError(rule.query, type=ServiceLabelingRule)
        dataset.rules.append(rule)
        self.__datasets__.update_dataset(dataset)
        return rule

    def compute_rule_metrics(
        self,
        dataset: ServiceTextClassificationDataset,
        rule_query: str,
        labels: Optional[List[str]] = None,
    ) -> Tuple[int, int, LabelingRuleSummary]:
        """Computes metrics for given rule query and optional label against a set of rules"""

        annotated_records = self._count_annotated_records(dataset)
        dataset_records = self.__records__.search_records(dataset, size=0).total
        metric_data = self.__records__.compute_metric(
            dataset=dataset,
            metric_id="labeling_rule",
            metric_params=dict(rule_query=rule_query, labels=labels),
        )

        return (
            dataset_records,
            annotated_records,
            LabelingRuleSummary.parse_obj(metric_data),
        )

    def _count_annotated_records(
        self, dataset: ServiceTextClassificationDataset
    ) -> int:
        results = self.__records__.search_records(
            dataset,
            size=0,
            search=DaoRecordsSearch(query=ServiceBaseRecordsQuery(has_annotation=True)),
        )
        return results.total

    def all_rules_metrics(
        self, dataset: ServiceTextClassificationDataset
    ) -> Tuple[int, int, DatasetLabelingRulesSummary]:
        annotated_records = self._count_annotated_records(dataset)
        dataset_records = self.__records__.search_records(dataset, size=0).total
        metric_data = self.__records__.compute_metric(
            dataset=dataset,
            metric_id="dataset_labeling_rules",
            metric_params=dict(queries=[r.query for r in dataset.rules]),
        )

        return (
            dataset_records,
            annotated_records,
            DatasetLabelingRulesSummary.parse_obj(metric_data),
        )

    def find_rule_by_query(
        self, dataset: ServiceTextClassificationDataset, rule_query: str
    ) -> ServiceLabelingRule:
        rule_query = rule_query.strip()
        for rule in dataset.rules:
            if rule.query == rule_query:
                return rule
        raise EntityNotFoundError(rule_query, type=ServiceLabelingRule)

    def replace_rule(
        self, dataset: ServiceTextClassificationDataset, rule: ServiceLabelingRule
    ):
        for idx, r in enumerate(dataset.rules):
            if r.query == rule.query:
                dataset.rules[idx] = rule
                break
        self.__datasets__.update_dataset(dataset)
