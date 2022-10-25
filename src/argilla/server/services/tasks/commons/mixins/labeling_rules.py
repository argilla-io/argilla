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

from typing import Generic, Iterable, List, Optional, Tuple, Type, TypeVar

from argilla.server.commons.models import BaseRulesSummary, BaseRuleSummary
from argilla.server.daos.models.records import DaoRecordsSearch
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.errors import EntityAlreadyExistsError, EntityNotFoundError
from argilla.server.services.datasets import DatasetsService, Rule, ServiceBaseDataset
from argilla.server.services.search.model import ServiceBaseRecordsQuery

RuleSummary = TypeVar("RuleSummary", bound=BaseRuleSummary)
RulesSummary = TypeVar("RulesSummary", bound=BaseRulesSummary)


class LabelingRulesMixin(Generic[Rule]):
    def __init__(
        self,
        datasets: DatasetsService,
        records: DatasetRecordsDAO,
    ):
        self.__datasets__ = datasets
        self.__records__ = records

    def get_labeling_rules(self, dataset: ServiceBaseDataset) -> Iterable[Rule]:
        return self.__datasets__.list_rules(dataset)

    def add_labeling_rule(
        self,
        dataset: ServiceBaseDataset,
        rule: Rule,
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
        self._prepare_rule_for_save(rule)
        self.__datasets__.add_rule(dataset, rule)

    def _prepare_rule_for_save(self, rule: Rule):
        pass

    def update_labeling_rule(
        self,
        dataset: ServiceBaseDataset,
        query_or_name: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **extra_data,
    ) -> Rule:
        found_rule = self.__datasets__.find_rule_by_query(dataset, query_or_name)

        if name:
            self._check_name_is_available(
                dataset,
                name=name,
                original_rule=found_rule,
            )
            found_rule.name = name

        extra_data = extra_data or {}
        if description is not None:
            found_rule.description = description

        data = {
            **found_rule.dict(exclude_unset=True),
            **extra_data,
        }
        new_rule = found_rule.parse_obj(data)

        self._prepare_rule_for_save(new_rule)
        self.__datasets__.replace_rule(dataset, new_rule)

        return found_rule

    def _check_name_is_available(
        self,
        dataset: ServiceBaseDataset,
        name: str,
        original_rule: Rule,
    ):
        try:
            rule = self.__datasets__.find_rule_by_query(
                dataset,
                query_or_name=name,
            )
            if rule != original_rule:
                raise EntityAlreadyExistsError(
                    name=name,
                    type=Rule,
                )
        except EntityNotFoundError:
            pass

    def find_labeling_rule(
        self,
        dataset: ServiceBaseDataset,
        query_or_name: str,
    ) -> Rule:
        return self.__datasets__.find_rule_by_query(
            dataset, query_or_name=query_or_name
        )

    def delete_labeling_rule(self, dataset: ServiceBaseDataset, rule_query: str):
        if rule_query.strip():
            return self.__datasets__.delete_rule(dataset, rule_query)

    def compute_rule_summary(
        self,
        dataset: ServiceBaseDataset,
        rule_query: str,
        summary_model: Type[RuleSummary] = BaseRuleSummary,
        **summary_params,
    ) -> Tuple[int, int, RuleSummary]:
        """Computes metrics for given rule query and optional label against a set of rules"""

        annotated_records = self._count_annotated_records(dataset)
        dataset_records = self.__records__.search_records(dataset, size=0).total
        metric_data = self.__records__.compute_metric(
            dataset=dataset,
            metric_id="labeling_rule",
            metric_params=dict(
                rule_query=rule_query,
                **(summary_params or {}),
            ),
        )

        return (
            dataset_records,
            annotated_records,
            summary_model.parse_obj(metric_data),
        )

    def compute_dataset_rules_summary(
        self,
        dataset: ServiceBaseDataset,
        summary_model: Type[RulesSummary] = BaseRulesSummary,
    ) -> Tuple[int, int, RulesSummary]:

        annotated_records = self._count_annotated_records(dataset)
        dataset_records = self.__records__.search_records(dataset, size=0).total
        queries = [r.query for r in dataset.rules]

        if not queries:
            return (
                dataset_records,
                annotated_records,
                summary_model(),
            )

        metric_data = self.__records__.compute_metric(
            dataset=dataset,
            metric_id="dataset_labeling_rules",
            metric_params=dict(queries=queries),
        )

        return (
            dataset_records,
            annotated_records,
            summary_model.parse_obj(metric_data),
        )

    def _count_annotated_records(
        self,
        dataset: ServiceBaseDataset,
    ) -> int:
        results = self.__records__.search_records(
            dataset,
            size=0,
            search=DaoRecordsSearch(query=ServiceBaseRecordsQuery(has_annotation=True)),
        )
        return results.total
