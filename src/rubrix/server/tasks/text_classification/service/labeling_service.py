from typing import List

from fastapi import Depends

from rubrix.server.commons.errors import EntityAlreadyExistsError, EntityNotFoundError
from rubrix.server.datasets.dao import DatasetsDAO, create_datasets_dao
from rubrix.server.datasets.model import BaseDatasetDB
from ..api.model import (
    LabelingRule,
    TextClassificationDatasetDB,
)


class LabelingService:

    _INSTANCE = None

    @classmethod
    def get_instance(cls, dao: DatasetsDAO = Depends(create_datasets_dao)):
        if cls._INSTANCE is None:
            cls._INSTANCE = cls(dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetsDAO):
        self.__dao__ = dao

    def _find_text_classification_dataset(
        self, dataset: BaseDatasetDB
    ) -> TextClassificationDatasetDB:
        found_ds = self.__dao__.find_by_id(
            dataset.id, ds_class=TextClassificationDatasetDB
        )
        if found_ds is None:
            raise EntityNotFoundError(dataset.name, dataset.__class__)
        return found_ds

    def list_rules(self, dataset: BaseDatasetDB) -> List[LabelingRule]:
        """List a set of rules for a given dataset"""
        found_ds = self._find_text_classification_dataset(dataset)
        return found_ds.rules

    def delete_rule(self, dataset: BaseDatasetDB, rule_query: str):
        """Delete a rule from a dataset by its defined query string"""
        found_ds = self._find_text_classification_dataset(dataset)
        new_rules_set = [r for r in found_ds.rules if r.query != rule_query]
        if len(found_ds.rules) != new_rules_set:
            found_ds.rules = new_rules_set
            self.__dao__.update_dataset(found_ds)

    def add_rule(self, dataset: BaseDatasetDB, rule: LabelingRule) -> LabelingRule:
        """Adds a rule to a dataset"""
        found_ds = self._find_text_classification_dataset(dataset)
        for r in found_ds.rules:
            if r.query == rule.query:
                raise EntityAlreadyExistsError(rule.query, type=LabelingRule)
        found_ds.rules.append(rule)
        self.__dao__.update_dataset(found_ds)
        return rule
