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

from argilla.server.daos.models.records import DaoRecordsSearch
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.services.search.model import ServiceBaseRecordsQuery
from argilla.server.services.tasks.text_classification.model import (
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
        records: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
    ):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(records)
        return cls._INSTANCE

    def __init__(self, records: DatasetRecordsDAO):
        self.__records__ = records

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
