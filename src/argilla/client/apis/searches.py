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

import dataclasses
from typing import List, Optional

from argilla.client.apis import AbstractApi
from argilla.client.models import Record
from argilla.client.sdk.datasets.models import TaskType
from argilla.client.sdk.text2text.models import Text2TextRecord
from argilla.client.sdk.text_classification.models import TextClassificationRecord
from argilla.client.sdk.token_classification.models import TokenClassificationRecord


@dataclasses.dataclass
class SearchResults:
    total: int

    records: List[Record]


class Searches(AbstractApi):

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
