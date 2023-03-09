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

from typing import Iterable, List, Optional, Tuple

from fastapi import Depends

from argilla.server.errors.base_errors import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    MissingDatasetRecordsError,
)
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.metrics import MetricsService
from argilla.server.services.search.model import (
    ServiceSearchResults,
    ServiceSortableField,
    ServiceSortConfig,
)
from argilla.server.services.search.service import SearchRecordsService
from argilla.server.services.storage.service import RecordsStorageService
from argilla.server.services.tasks.commons import BulkResponse
from argilla.server.services.tasks.text_classification.metrics import (
    TextClassificationMetrics,
)
from argilla.server.services.tasks.text_classification.model import (
    DatasetLabelingRulesMetricsSummary,
    DatasetLabelingRulesSummary,
    LabelingRuleMetricsSummary,
    LabelingRuleSummary,
    ServiceLabelingRule,
    ServiceTextClassificationDataset,
    ServiceTextClassificationQuery,
    ServiceTextClassificationRecord,
)


class TextClassificationService:
    """
    Text classification service

    """

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
        storage: RecordsStorageService = Depends(RecordsStorageService.get_instance),
        search: SearchRecordsService = Depends(SearchRecordsService.get_instance),
    ) -> "TextClassificationService":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(datasets=datasets, metrics=metrics, storage=storage, search=search)
        return cls._INSTANCE

    def __init__(
        self,
        datasets: DatasetsService,
        metrics: MetricsService,
        storage: RecordsStorageService,
        search: SearchRecordsService,
    ):
        self.__storage__ = storage
        self.__search__ = search
        self.__metrics__ = metrics
        self.__datasets__ = datasets

    async def add_records(
        self,
        dataset: ServiceTextClassificationDataset,
        records: List[ServiceTextClassificationRecord],
    ):
        # TODO(@frascuchon): This will moved to dataset settings validation once DatasetSettings join the game!
        self._check_multi_label_integrity(dataset, records)

        failed = await self.__storage__.store_records(
            dataset=dataset,
            records=records,
            record_type=ServiceTextClassificationRecord,
        )
        return BulkResponse(
            dataset=dataset.name,
            processed=len(records),
            failed=failed,
        )

    def search(
        self,
        dataset: ServiceTextClassificationDataset,
        query: ServiceTextClassificationQuery,
        sort_by: List[ServiceSortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
    ) -> ServiceSearchResults:
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

        metrics = [
            TextClassificationMetrics.find_metric(id)
            for id in {
                "words_cloud",
                "predicted_by",
                "predicted_as",
                "annotated_by",
                "annotated_as",
                "error_distribution",
                "status_distribution",
                "metadata",
                "score",
            }
        ]

        results = self.__search__.search(
            dataset,
            query=query,
            record_type=ServiceTextClassificationRecord,
            record_from=record_from,
            size=size,
            exclude_metrics=exclude_metrics,
            metrics=metrics,
            sort_config=ServiceSortConfig(
                sort_by=sort_by,
            ),
        )

        if results.metrics:
            results.metrics["words"] = results.metrics.get("words_cloud", {})
            results.metrics["status"] = results.metrics["status_distribution"]
            results.metrics["predicted"] = results.metrics["error_distribution"]
            results.metrics["predicted"].pop("unknown", None)

        return results

    def read_dataset(
        self,
        dataset: ServiceTextClassificationDataset,
        query: Optional[ServiceTextClassificationQuery] = None,
        id_from: Optional[str] = None,
        limit: int = 1000,
    ) -> Iterable[ServiceTextClassificationRecord]:
        """
        Scan a dataset records

        Parameters
        ----------
        dataset:
            The dataset name
        query:
            If provided, scan will retrieve only records matching
            the provided query filters. Optional
        id_from:
            If provided, read the samples after this record ID
        limit:
            Batch size to scan, only used if `id_from` is specified

        """
        yield from self.__search__.scan_records(
            dataset,
            query=query,
            record_type=ServiceTextClassificationRecord,
            id_from=id_from,
            limit=limit,
        )

    def _check_multi_label_integrity(
        self,
        dataset: ServiceTextClassificationDataset,
        records: List[ServiceTextClassificationRecord],
    ):
        is_multi_label_dataset = self._is_dataset_multi_label(dataset)
        if is_multi_label_dataset is not None:
            is_multi_label = records[0].multi_label
            assert (
                is_multi_label == is_multi_label_dataset
            ), "You cannot pass {labels_type} records for this dataset. " "Stored records are {labels_type}".format(
                labels_type="multi-label" if is_multi_label else "single-label"
            )

    def _is_dataset_multi_label(self, dataset: ServiceTextClassificationDataset) -> Optional[bool]:
        try:
            results = self.__search__.search(
                dataset,
                record_type=ServiceTextClassificationRecord,
                size=1,
            )
        except MissingDatasetRecordsError:  # No records index yet
            return None
        if results.records:
            return results.records[0].multi_label

    def find_labeling_rule(
        self, dataset: ServiceTextClassificationDataset, rule_query: str, error_on_missing: bool = True
    ) -> Optional[ServiceLabelingRule]:
        rule_query = rule_query.strip()
        for rule in dataset.rules:
            if rule.query == rule_query:
                return rule
        if error_on_missing:
            raise EntityNotFoundError(rule_query, type=ServiceLabelingRule)

    def list_labeling_rules(self, dataset: ServiceTextClassificationDataset) -> Iterable[ServiceLabelingRule]:
        return dataset.rules

    def add_labeling_rule(self, dataset: ServiceTextClassificationDataset, rule: ServiceLabelingRule) -> None:
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
        if self.find_labeling_rule(dataset, rule_query=rule.query, error_on_missing=False):
            raise EntityAlreadyExistsError(rule.query, type=ServiceLabelingRule)

        dataset.rules.append(rule)
        self.__datasets__.raw_dataset_update(dataset)

    def update_labeling_rule(
        self,
        dataset: ServiceTextClassificationDataset,
        rule_query: str,
        labels: List[str],
        description: Optional[str] = None,
    ) -> ServiceLabelingRule:
        found_rule = self.find_labeling_rule(dataset, rule_query)

        found_rule.labels = labels
        found_rule.label = labels[0] if len(labels) == 1 else None
        if description is not None:
            found_rule.description = description

        self.__normalized_rule__(found_rule)
        for idx, r in enumerate(dataset.rules):
            if r.query == found_rule.query:
                dataset.rules[idx] = found_rule
                break
        self.__datasets__.raw_dataset_update(dataset)

        return found_rule

    def delete_labeling_rule(self, dataset: ServiceTextClassificationDataset, rule_query: str):
        """Delete a rule from a dataset by its defined query string"""
        new_rules_set = [r for r in dataset.rules if r.query != rule_query]
        if len(dataset.rules) != new_rules_set:
            dataset.rules = new_rules_set
            self.__datasets__.raw_dataset_update(dataset)

    def compute_labeling_rule(
        self,
        dataset: ServiceTextClassificationDataset,
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
            rule = self.find_labeling_rule(dataset, rule_query=rule_query, error_on_missing=False)
            if rule:
                labels = rule.labels

        metric_data = self.__metrics__.summarize_metric(
            dataset=dataset,
            metric=TextClassificationMetrics.find_metric("labeling_rule"),
            rule_query=rule_query,
            labels=labels,
        )
        annotated = self.__metrics__.annotated_records(dataset)
        total = self.__metrics__.total_records(dataset)

        metrics = LabelingRuleSummary.parse_obj(metric_data)

        coverage = metrics.covered_records / total if total > 0 else None
        coverage_annotated = metrics.annotated_covered_records / annotated if annotated > 0 else None

        return LabelingRuleMetricsSummary(
            total_records=total,
            annotated_records=annotated,
            coverage=coverage,
            coverage_annotated=coverage_annotated,
            correct=metrics.correct_records if annotated > 0 else None,
            incorrect=metrics.incorrect_records if annotated > 0 else None,
            precision=metrics.precision if annotated > 0 else None,
        )

    def compute_all_labeling_rules(self, dataset: ServiceTextClassificationDataset):
        total, annotated, metrics = self._compute_all_lb_rules_metrics(dataset)
        coverage = metrics.covered_records / total if total else None
        coverage_annotated = metrics.annotated_covered_records / annotated if annotated else None
        return DatasetLabelingRulesMetricsSummary(
            coverage=coverage,
            coverage_annotated=coverage_annotated,
            total_records=total,
            annotated_records=annotated,
        )

    def _compute_all_lb_rules_metrics(
        self, dataset: ServiceTextClassificationDataset
    ) -> Tuple[int, int, DatasetLabelingRulesSummary]:
        annotated_records = self.__metrics__.annotated_records(dataset)
        dataset_records = self.__metrics__.total_records(dataset)
        metric_data = self.__metrics__.summarize_metric(
            dataset=dataset,
            metric=TextClassificationMetrics.find_metric(id="dataset_labeling_rules"),
            queries=[r.query for r in dataset.rules],
        )

        return (
            dataset_records,
            annotated_records,
            DatasetLabelingRulesSummary.parse_obj(metric_data),
        )

    @staticmethod
    def __normalized_rule__(rule: ServiceLabelingRule) -> ServiceLabelingRule:
        if rule.labels and len(rule.labels) == 1:
            rule.label = rule.labels[0]
        elif rule.label and not rule.labels:
            rule.labels = [rule.label]

        return rule
