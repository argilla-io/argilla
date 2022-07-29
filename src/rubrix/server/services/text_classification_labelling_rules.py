from typing import List, Optional, Tuple

from fastapi import Depends
from pydantic import BaseModel, Field

from rubrix.server.apis.v0.models.text_classification import (
    LabelingRule,
    TextClassificationDatasetDB,
)
from rubrix.server.daos.datasets import DatasetsDAO
from rubrix.server.daos.models.records import BaseSearchQuery, RecordSearch
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.errors import EntityAlreadyExistsError, EntityNotFoundError


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

    def list_rules(self, dataset: TextClassificationDatasetDB) -> List[LabelingRule]:
        """List a set of rules for a given dataset"""
        return dataset.rules

    def delete_rule(self, dataset: TextClassificationDatasetDB, rule_query: str):
        """Delete a rule from a dataset by its defined query string"""
        new_rules_set = [r for r in dataset.rules if r.query != rule_query]
        if len(dataset.rules) != new_rules_set:
            dataset.rules = new_rules_set
            self.__datasets__.update_dataset(dataset)

    def add_rule(
        self, dataset: TextClassificationDatasetDB, rule: LabelingRule
    ) -> LabelingRule:
        """Adds a rule to a dataset"""
        for r in dataset.rules:
            if r.query == rule.query:
                raise EntityAlreadyExistsError(rule.query, type=LabelingRule)
        dataset.rules.append(rule)
        self.__datasets__.update_dataset(dataset)
        return rule

    def compute_rule_metrics(
        self,
        dataset: TextClassificationDatasetDB,
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

    def _count_annotated_records(self, dataset: TextClassificationDatasetDB) -> int:
        results = self.__records__.search_records(
            dataset,
            size=0,
            search=RecordSearch(query=BaseSearchQuery(has_annotation=True)),
        )
        return results.total

    def all_rules_metrics(
        self, dataset: TextClassificationDatasetDB
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
        self, dataset: TextClassificationDatasetDB, rule_query: str
    ) -> LabelingRule:
        rule_query = rule_query.strip()
        for rule in dataset.rules:
            if rule.query == rule_query:
                return rule
        raise EntityNotFoundError(rule_query, type=LabelingRule)

    def replace_rule(self, dataset: TextClassificationDatasetDB, rule: LabelingRule):
        for idx, r in enumerate(dataset.rules):
            if r.query == rule.query:
                dataset.rules[idx] = rule
                break
        self.__datasets__.update_dataset(dataset)
