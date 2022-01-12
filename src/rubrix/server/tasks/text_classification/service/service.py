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

from typing import Iterable, List, Optional

from fastapi import Depends

from rubrix.server.commons.errors import EntityNotFoundError, MissingInputParamError
from rubrix.server.commons.es_helpers import sort_by2elasticsearch
from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons import (
    BulkResponse,
    EsRecordDataFieldNames,
    SortableField,
)
from rubrix.server.tasks.commons.dao import extends_index_dynamic_templates
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO, dataset_records_dao
from rubrix.server.tasks.commons.dao.model import RecordSearch
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.text_classification.api.model import (
    CreationTextClassificationRecord,
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationQuery,
    TextClassificationRecord,
    TextClassificationSearchAggregations,
    TextClassificationSearchResults,
)
from rubrix.server.tasks.text_classification.service.labeling_service import (
    LabelingService,
)

extends_index_dynamic_templates(
    {"inputs": {"path_match": "inputs.*", "mapping": {"type": "text"}}}
)


class TextClassificationService:
    """
    Text classification service

    """

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        dao: DatasetRecordsDAO = Depends(dataset_records_dao),
        labeling: LabelingService = Depends(LabelingService.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ) -> "TextClassificationService":
        """
        Creates a service instance for text classification operations

        Parameters
        ----------
        dao:
            The dataset records dao dependency
        labeling:
            The labeling service dependency
        metrics:
            The metrics service dependency

        Returns
        -------
            A dataset records service instance
        """
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao, metrics, labeling=labeling)
        return cls._INSTANCE

    def __init__(
        self,
        dao: DatasetRecordsDAO,
        metrics: MetricsService,
        labeling: LabelingService,
    ):
        self.__dao__ = dao
        self.__metrics__ = metrics
        self.__labeling__ = labeling

    def add_records(
        self,
        dataset: Dataset,
        records: List[CreationTextClassificationRecord],
    ):
        self._check_multi_label_integrity(dataset, records)
        self.__metrics__.build_records_metrics(dataset, records)
        failed = self.__dao__.add_records(
            dataset=dataset, records=records, record_class=TextClassificationRecord
        )
        return BulkResponse(dataset=dataset.name, processed=len(records), failed=failed)

    def search(
        self,
        dataset: Dataset,
        query: TextClassificationQuery,
        sort_by: List[SortableField],
        record_from: int = 0,
        size: int = 100,
        exclude_metrics: bool = True,
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
        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(
                query=query.as_elasticsearch(),
                sort=sort_by2elasticsearch(
                    sort_by,
                    valid_fields=[
                        "metadata",
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
            ),
            size=size,
            record_from=record_from,
            exclude_fields=["metrics"] if exclude_metrics else None,
        )
        return TextClassificationSearchResults(
            total=results.total,
            records=[TextClassificationRecord.parse_obj(r) for r in results.records],
            aggregations=TextClassificationSearchAggregations(
                **results.aggregations,
                words=results.words,
                metadata=results.metadata or {},
            )
            if results.aggregations
            else None,
        )

    def read_dataset(
        self,
        dataset: Dataset,
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
        for db_record in self.__dao__.scan_dataset(
            dataset, search=RecordSearch(query=query.as_elasticsearch())
        ):
            yield TextClassificationRecord.parse_obj(db_record)

    def _check_multi_label_integrity(
        self, dataset: Dataset, records: List[TextClassificationRecord]
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

    def _is_dataset_multi_label(self, dataset: Dataset) -> Optional[bool]:
        results = self.__dao__.search_records(
            dataset,
            search=RecordSearch(include_default_aggregations=False),
            size=1,
            exclude_fields=["metrics", "metadata"],
        )
        records = [TextClassificationRecord.parse_obj(r) for r in results.records]
        if records:
            return records[0].multi_label

    def get_labeling_rules(self, dataset: Dataset) -> Iterable[LabelingRule]:
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

    def add_labeling_rule(self, dataset: Dataset, rule: LabelingRule) -> None:
        """
        Adds a labeling rule

        Parameters
        ----------
        dataset:
            The dataset

        rule:
            The rule

        """
        is_multi_label_dataset = self._is_dataset_multi_label(dataset)
        if is_multi_label_dataset is not None:
            assert (
                not is_multi_label_dataset
            ), "Labeling rules are not supported for multi-label datasets"
        self.__labeling__.add_rule(dataset, rule)

    def update_labeling_rule(
        self,
        dataset: Dataset,
        rule_query: str,
        label: str,
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

        found_rule.label = label
        if description is not None:
            found_rule.description = description

        self.__labeling__.replace_rule(dataset, found_rule)
        return found_rule

    def find_labeling_rule(self, dataset: Dataset, rule_query: str):
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

    def delete_labeling_rule(self, dataset: Dataset, rule_query: str):
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
        dataset: Dataset,
        rule_query: str,
        label: Optional[str],
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
        label:
            Label used for the rule metrics. If not provided and no rule was stored with the
            provided query, no precision will be computed.
            Otherwise, the label from the stored rule will be used to compute the metrics.

        Returns
        -------

            Metrics summary for rule and label

        """

        rule_query = rule_query.strip()

        if label is None:
            for rule in self.get_labeling_rules(dataset):
                if rule.query == rule_query:
                    label = rule.label
                    break

        total, annotated, metrics = self.__labeling__.compute_rule_metrics(
            dataset, rule_query=rule_query, label=label
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

    def compute_overall_rules_metrics(self, dataset: Dataset):
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
