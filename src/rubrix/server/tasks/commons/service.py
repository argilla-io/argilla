from typing import Iterable, List, Optional, TypeVar

from rubrix.client.models import BulkResponse
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.tasks.commons import BaseRecord, BaseSearchResults, SortableField
from rubrix.server.tasks.search.model import BaseSearchQuery

SVCDataset = TypeVar("SVCDataset", bound=DatasetDB)
SVCRecord = TypeVar("SVCRecord", bound=BaseRecord)
SVCQuery = TypeVar("SVCQuery", bound=BaseSearchQuery)
SVCSearchResults = TypeVar("SVCSearchResults", bound=BaseSearchResults)
SVCRule = TypeVar("SVCRule")
SVCDatasetRulesMetrics = TypeVar("SVCDatasetRulesMetrics")
SVCRuleMetrics = TypeVar("SVCRuleMetrics")


class TaskService:
    @classmethod
    def get_instance(cls, *args, **kwargs) -> "TaskService":
        raise NotImplementedError()

    async def add_records(
        self,
        dataset: SVCDataset,
        records: List[SVCRecord],
    ) -> BulkResponse:
        raise NotImplementedError()

    async def search(
        self,
        dataset: SVCDataset,
        query: Optional[SVCQuery] = None,
        sort_by: List[SortableField] = None,
        record_from: int = 0,
        size: int = 100,
    ) -> SVCSearchResults:
        raise NotImplementedError()

    async def read_dataset(
        self,
        dataset: SVCDataset,
        query: Optional[SVCQuery] = None,
    ) -> Iterable[SVCRecord]:
        raise NotImplementedError()

    async def get_labeling_rules(self, dataset: SVCDataset) -> Iterable[SVCRule]:
        raise NotImplementedError()

    async def add_labeling_rule(self, dataset: SVCDataset, rule: SVCRule) -> SVCRule:
        raise NotImplementedError()

    async def find_labeling_rule(self, dataset: SVCDataset, rule_query: str) -> SVCRule:
        raise NotImplementedError()

    async def update_labeling_rule(
        self, dataset: SVCDataset, rule_query: str, **kwargs
    ) -> SVCRule:
        raise NotImplementedError()

    async def delete_labeling_rule(self, dataset: SVCDataset, rule_query: str) -> None:
        raise NotImplementedError()

    async def compute_overall_rules_metrics(
        self, dataset: SVCDataset
    ) -> SVCDatasetRulesMetrics:
        raise NotImplementedError()

    async def compute_rule_metrics(
        self,
        dataset: SVCDataset,
        rule_query: str,
        labels: Optional[List[str]] = None,
    ) -> SVCRuleMetrics:
        raise NotImplementedError()
