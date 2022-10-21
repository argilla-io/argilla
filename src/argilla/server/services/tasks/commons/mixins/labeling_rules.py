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

from typing import Generic, Iterable, Optional

from argilla.server import helpers
from argilla.server.services.datasets import DatasetsService, Rule, ServiceBaseDataset


class LabelingRulesMixin(Generic[Rule]):
    def __init__(self, datasets: DatasetsService):
        self.__datasets__ = datasets

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
        description: Optional[str] = None,
        **extra_data,
    ) -> Rule:
        found_rule = self.__datasets__.find_rule_by_query(dataset, query_or_name)

        extra_data = helpers.exclude_nones_from_dict(extra_data or {})
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
