import dataclasses
from typing import List, Optional

from rubrix.client.apis import AbstractAPI
from rubrix.client.models import Record
from rubrix.client.sdk.datasets.models import TaskType
from rubrix.client.sdk.text2text.models import Text2TextRecord
from rubrix.client.sdk.text_classification.models import TextClassificationRecord
from rubrix.client.sdk.token_classification.models import TokenClassificationRecord


@dataclasses.dataclass
class SearchResults:
    total: int

    records: List[Record]


class Searches(AbstractAPI):

    _API_URL_PATTERN = "/api/datasets/{name}/{task}:search"

    def search_records(
        self,
        name: str,
        task: TaskType,
        query: Optional[str],
        size: Optional[int] = None,
    ):
        """
        Searches records over a dataset

        Args:
            name: The dataset name
            task: The dataset task type
            query: The query string
            size: If provided, only the provided number of records will be fetched

        Returns:
            An instance of ``SearchResults`` class containing the search results
        """

        if task == TaskType.text_classification:
            record_class = TextClassificationRecord
        elif task == TaskType.token_classification:
            record_class = TokenClassificationRecord
        elif task == TaskType.text2text:
            record_class = Text2TextRecord
        else:
            raise ValueError(f"Task {task} not supported")

        url = self._API_URL_PATTERN.format(name=name, task=task)
        if size:
            url += f"{url}?size={size}"

        query_request = {}
        if query:
            query_request["query_text"] = query

        response = self.__client__.post(
            path=url,
            json={"query": query_request},
        )

        return SearchResults(
            total=response["total"],
            records=[
                record_class.parse_obj(r).to_client() for r in response["records"]
            ],
        )
