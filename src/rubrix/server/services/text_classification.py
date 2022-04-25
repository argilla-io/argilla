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

from typing import Any, Dict, Iterable, List, Optional, Type

from fastapi import Depends

from rubrix.server.apis.v0.models.commons.model import (
    BulkResponse,
    EsRecordDataFieldNames,
    SortableField,
)
from rubrix.server.apis.v0.models.metrics.base import BaseMetric, BaseTaskMetrics
from rubrix.server.apis.v0.models.text_classification import (
    CreationTextClassificationRecord,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationDatasetDB,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationRecordDB,
    TextClassificationSearchAggregations,
    TextClassificationSearchResults,
)
from rubrix.server.errors.base_errors import MissingDatasetRecordsError
from rubrix.server.services.search.model import SortConfig
from rubrix.server.services.search.service import SearchRecordsService
from rubrix.server.services.storage.service import RecordsStorageService
from rubrix.server.services.text_classification_labelling_rules import LabelingService


class TextClassificationService:
    """
    Text classification service

    """

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        storage: RecordsStorageService = Depends(RecordsStorageService.get_instance),
        labeling: LabelingService = Depends(LabelingService.get_instance),
        search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
    ) -> "TextClassificationService":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(storage, labeling=labeling, search=search)
        return cls._INSTANCE

    def __init__(
        self,
        storage: RecordsStorageService,
        search: SearchRecordsService,
        labeling: LabelingService,
    ):
        self.__storage__ = storage
        self.__search__ = search
        self.__labeling__ = labeling

    def add_records(
        self,
        dataset: TextClassificationDatasetDB,
        mappings: Dict[str, Any],
        records: List[CreationTextClassificationRecord],
        metrics: Type[BaseTaskMetrics],
    ):
        # TODO(@frascuchon): This will moved to dataset settings validation once DatasetSettings join the game!
        self._check_multi_label_integrity(dataset, records)

        failed = self.__storage__.store_records(
            dataset=dataset,
            mappings=mappings,
            records=records,
            record_type=TextClassificationRecordDB,
            metrics=metrics,
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: TextClassificationDatasetDB,
        query: TextClassificationQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
        metrics: Optional[List[BaseMetric]] = None,
    ) -> TextClassificationSearchResults:
        """
        Run a search in a dataset

        Parameters
        ----------
        dataset:
            The records dataset
        query:
            The search parameters
        sort_by:
            The sort by list
        record_from:
            The record from return results
        size:
            The max number of records to return

        Returns
        -------
            The matched records with aggregation info for specified task_meta.py

        """

        results = self.__search__.search(
            dataset,
            query=query,
            record_type=TextClassificationRecord,
            record_from=record_from,
            size=size,
            exclude_metrics=exclude_metrics,
            metrics=metrics,
            sort_config=SortConfig(
                sort_by=sort_by,
                valid_fields=[
                    "metadata",
                    EsRecordDataFieldNames.last_updated,
                    EsRecordDataFieldNames.score,
                    EsRecordDataFieldNames.predicted,
                    EsRecordDataFieldNames.predicted_as,
                    EsRecordDataFieldNames.predicted_by,
                    EsRecordDataFieldNames.annotated_as,
                    EsRecordDataFieldNames.annotated_by,
                    EsRecordDataFieldNames.status,
                    EsRecordDataFieldNames.event_timestamp,
                ],
            ),
        )

        if results.metrics:
            results.metrics["words"] = results.metrics["words_cloud"]
            results.metrics["status"] = results.metrics["status_distribution"]
            results.metrics["predicted"] = results.metrics["error_distribution"]
            results.metrics["predicted"].pop("unknown", None)

        return TextClassificationSearchResults(
            total=results.total,
            records=results.records,
            aggregations=TextClassificationSearchAggregations.parse_obj(results.metrics)
            if results.metrics
            else None,
        )

    def read_dataset(
        self,
        dataset: TextClassificationDatasetDB,
        query: Optional[TextClassificationQuery] = None,
    ) -> Iterable[TextClassificationRecord]:
        """
        Scan a dataset records

        Parameters
        ----------
        dataset:
            The dataset name
        query:
            If provided, scan will retrieve only records matching
            the provided query filters. Optional

        """
        yield from self.__search__.scan_records(
            dataset, query=query, record_type=TextClassificationRecord
        )

    def _check_multi_label_integrity(
        self,
        dataset: TextClassificationDatasetDB,
        records: List[CreationTextClassificationRecord],
    ):
        is_multi_label_dataset = self._is_dataset_multi_label(dataset)
        if is_multi_label_dataset is not None:
            is_multi_label = records[0].multi_label
            assert is_multi_label == is_multi_label_dataset, (
                "You cannot pass {labels_type} records for this dataset. "
                "Stored records are {labels_type}".format(
                    labels_type="multi-label" if is_multi_label else "single-label"
                )
            )

    def _is_dataset_multi_label(
        self, dataset: TextClassificationDatasetDB
    ) -> Optional[bool]:
        try:
            results = self.__search__.search(
                dataset,
                record_type=TextClassificationRecord,
                size=1,
            )
        except MissingDatasetRecordsError:  # No records index yet
            return None
        if results.records:
            return results.records[0].multi_label

    def get_labeling_rules(
        self, dataset: TextClassificationDatasetDB
    ) -> Iterable[LabelingRule]:
        """
        Gets rules for a given dataset

        Parameters
        ----------
        dataset:
            The dataset

        Returns
        -------
            A list of labeling rules for a given dataset

        """
        return self.__labeling__.list_rules(dataset)

    def add_labeling_rule(
        self, dataset: TextClassificationDatasetDB, rule: LabelingRule
    ) -> None:
        """
        Adds a labeling rule

        Parameters
        ----------
        dataset:
            The dataset

        rule:
            The rule
        """
        self.__normalized_rule__(rule)
        self.__labeling__.add_rule(dataset, rule)

    def update_labeling_rule(
        self,
        dataset: TextClassificationDatasetDB,
        rule_query: str,
        labels: List[str],
        description: Optional[str] = None,
    ) -> LabelingRule:
        """
        Update a labeling rule. Updatable fields are label and/or description

        Args:
            dataset: The dataset
            rule_query: The labeling rule
            label: The new rule label
            description: If provided, the new rule description

        Returns:
            Updated labeling rule

        """
        found_rule = self.__labeling__.find_rule_by_query(dataset, rule_query)

        found_rule.labels = labels
        found_rule.label = labels[0] if len(labels) == 1 else None
        if description is not None:
            found_rule.description = description

        self.__normalized_rule__(found_rule)
        self.__labeling__.replace_rule(dataset, found_rule)
        return found_rule

    def find_labeling_rule(self, dataset: TextClassificationDatasetDB, rule_query: str):
        """
        Find a labeling rule given a rule query string

        Args:
            dataset: The dataset
            rule_query:  The query string

        Returns:
            Found labeling rule.
            If rule was not found EntityNotFoundError is raised
        """
        return self.__labeling__.find_rule_by_query(dataset, rule_query=rule_query)

    def delete_labeling_rule(
        self, dataset: TextClassificationDatasetDB, rule_query: str
    ):
        """
        Deletes a rule from a dataset.

        Nothing happens if the rule does not exist in dataset.

        Parameters
        ----------

        dataset:
            The dataset

        rule_query:
            The rule query

        """
        if rule_query.strip():
            return self.__labeling__.delete_rule(dataset, rule_query)

    def compute_rule_metrics(
        self,
        dataset: TextClassificationDatasetDB,
        rule_query: str,
        labels: Optional[List[str]] = None,
    ) -> LabelingRuleMetricsSummary:
        """
        Compute metrics for a given rule. It's not necessary that query rule
        is created in dataset. Basic computed rules are:

        coverage, correct[*], incorrect[*], precision[*]

        [*]: computed metrics only if label is provided or rule already created in dataset

        Parameters
        ----------
        dataset:
            The dataset
        rule_query:
            The provided rule query. If already created in dataset, the ``label``
            param will be omitted
        labels:
            Label used for the rule metrics. If not provided and no rule was stored with the
            provided query, no precision will be computed.
            Otherwise, the labels from the stored rule will be used to compute the metrics.

        Returns
        -------

            Metrics summary for rule and labels

        """

        rule_query = rule_query.strip()

        if labels is None:
            for rule in self.get_labeling_rules(dataset):
                if rule.query == rule_query:
                    labels = rule.labels
                    break

        total, annotated, metrics = self.__labeling__.compute_rule_metrics(
            dataset, rule_query=rule_query, labels=labels
        )

        coverage = metrics.covered_records / total if total > 0 else None
        coverage_annotated = (
            metrics.annotated_covered_records / annotated if annotated > 0 else None
        )
        return LabelingRuleMetricsSummary(
            total_records=total,
            annotated_records=annotated,
            coverage=coverage,
            coverage_annotated=coverage_annotated,
            correct=metrics.correct_records if annotated > 0 else None,
            incorrect=metrics.incorrect_records if annotated > 0 else None,
            precision=metrics.precision if annotated > 0 else None,
        )

    def compute_overall_rules_metrics(self, dataset: TextClassificationDatasetDB):
        total, annotated, metrics = self.__labeling__.all_rules_metrics(dataset)
        coverage = metrics.covered_records / total if total else None
        coverage_annotated = (
            metrics.annotated_covered_records / annotated if annotated else None
        )
        return DatasetLabelingRulesMetricsSummary(
            coverage=coverage,
            coverage_annotated=coverage_annotated,
            total_records=total,
            annotated_records=annotated,
        )

    @staticmethod
    def __normalized_rule__(rule: LabelingRule) -> LabelingRule:
        if rule.labels and len(rule.labels) == 1:
            rule.label = rule.labels[0]
        elif rule.label and not rule.labels:
            rule.labels = [rule.label]

        return rule
