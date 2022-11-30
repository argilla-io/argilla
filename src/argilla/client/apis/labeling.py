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
from typing import Any, Dict, Iterable, List, Optional, Tuple

from argilla.client.apis import AbstractApi


@dataclasses.dataclass
class Rule:
    label: str
    query: str


class TokenClassificationLabelingRules(AbstractApi):
    """Api client component to handle with labeling rules endpoints"""

    _API_URL_PATTERN = "/api/datasets/{name}/TokenClassification/labeling/rules"

    def rule_summary(
        self,
        dataset: str,
        rule: Rule,
    ) -> Dict[str, Dict[str, Any]]:
        """Computes the rule summary for a given dataset and return the raw summary"""
        url = self._API_URL_PATTERN.format(name=dataset)
        url += f"/{rule.query}/summary?{rule.label}"

        response = self.__client__.get(path=url)
        return response

    def rule_annotations(
        self,
        dataset: str,
        rule: Rule,
        ids: Optional[List[str]],
        chunk_size: int = 500,
    ) -> Iterable[str, List[Tuple[str, int, int]]]:
        """Computes span annotations for a given rule"""
        pass

        url = self._API_URL_PATTERN.format(name=dataset)
        url += f"/{rule.query}/search?{rule.label}&size={chunk_size}"
        body = {"record_ids": ids} if ids else None

        next_record = yield from self._fetch_annotations_chunk(url=url, body=body)
        while next_record:
            next_record = yield from self._fetch_annotations_chunk(
                url=url,
                body=body,
                next_record=next_record,
            )

    def _fetch_annotations_chunk(
        self,
        *,
        url: str,
        body: Optional[dict],
        next_record: Optional[str] = None,
    ) -> Optional[str]:

        url_copy = url
        if next_record:
            url_copy += f"&next{next_record}"

        response = self.__client__.post(
            path=url_copy,
            json=body,
        )
        for data in response["records"]:
            yield data["id"], [
                (
                    entity["label"],
                    entity["start"],
                    entity["end"],
                )
                for entity in data["entities"]
            ]
        return response.get("next")

    def _normalize_annotations(self, response):
        pass
