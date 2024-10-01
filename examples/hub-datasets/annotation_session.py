import random
from collections import defaultdict
from typing import Iterable, Literal

from hub_dataset import HubDataset


class MockAnnotationsStore:
    def __init__(self):
        self.__annotations = defaultdict(list)

    def add(self, row_idx: int, user, **annotations):
        self.__annotations[row_idx].append((annotations, user))

    def list_by_row_idx(self, row_idx: int) -> list:
        return self.__annotations[row_idx]

    def list(self) -> dict:
        return {k: v for k, v in self.__annotations.items()}

    def list_by_user(self, user: str) -> list:
        for row_idx, annotations_user in self.__annotations.items():
            for annotations, _user in annotations_user:
                if _user == user:
                    yield row_idx, annotations


class AnnotationSession:
    """An annotation session for a dataset. The session allows users to annotate rows in the dataset."""

    _annotations = MockAnnotationsStore()

    def __init__(self, dataset: HubDataset):
        self.dataset = dataset

    def annotation_status(self, row_idx: int) -> Literal["pending", "annotated"]:
        """Get the annotation status for a row"""
        return "annotated" if self.get_row_annotations(row_idx) else "pending"

    def annotate(self, row_idx: int, user: str, **annotations) -> None:
        """Annotate a row"""
        self._annotations.add(row_idx=row_idx, user=user, **annotations)

    def get_row_annotations(self, row_idx: int) -> list:
        """Get the annotations for a row"""
        return self._annotations.list_by_row_idx(row_idx)

    def annotated_rows(self, user: str, limit: int | None = None) -> Iterable[dict]:
        """Get the annotated records for a user"""

        limit = min(limit or 500, 500)

        for idx, annotations in self._annotations.list_by_user(user):
            if limit == 0:
                break

            yield self.dataset.get(idx)
            limit -= 1

    def pending_rows_batch(self, user: str, limit: int | None = None) -> Iterable[dict]:
        """Get a batch of pending records for a user"""

        limit = min(limit or 500, 500)
        local_random = random.Random(user)

        if limit >= self._pending_records_count():
            records = list(self.list(limit=limit, status="pending"))

            local_random.shuffle(records)
            for r in records:
                yield r
        else:
            total_number_of_rows = self.dataset.size()["num_rows"]

            count = 0
            while count < limit < self._pending_records_count():
                row_idx = local_random.randint(0, total_number_of_rows)
                if self.annotation_status(row_idx) == "pending":
                    yield self.dataset.get(row_idx)
                    count += 1

    def list(
        self,
        limit: int | None = None,
        status: Literal["pending", "annotated"] = "pending",
    ) -> Iterable[dict]:
        """List the records in the dataset"""

        count = 0
        if status == "pending":
            rows = self.dataset.iterable_rows()

        else:
            rows = (self.dataset.get(idx) for idx in self._annotations.list().keys())

        for r in rows:
            if count == limit:
                break

            if self.annotation_status(r["row_idx"]) == status:
                count += 1
                yield r

    def filter(
        self,
        where: str,
        limit: int | None = None,
        status: Literal["pending", "annotated"] = "pending",
        **kwargs,
    ) -> Iterable[dict]:
        """Filter the records in the dataset"""

        count = 0
        for r in self.dataset.iterable_filter(where=where, **kwargs):
            if count == limit:
                break

            if self.annotation_status(r["row_idx"]) == status:
                count += 1
                yield r

    def search(
        self,
        query: str,
        limit: int | None = None,
        status: Literal["pending", "annotated"] = "pending",
        **kwargs,
    ) -> Iterable[dict]:
        """Search the records in the dataset"""

        count = 0
        for r in self.dataset.iterable_search(query=query, **kwargs):
            if count == limit:
                break

            if self.annotation_status(r["row_idx"]) == status:
                count += 1
                yield r

    def _pending_records_count(self) -> int:
        return self.dataset.size()["num_rows"] - self._annotated_records_count()

    def _annotated_records_count(self) -> int:
        return len(self._annotations.list())
