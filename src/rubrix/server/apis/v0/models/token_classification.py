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
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from rubrix.server.apis.v0.models.datasets import UpdateDatasetRequest
from rubrix.server.backend.search.model import SortableField
from rubrix.server.services.tasks.token_classification.model import (
    CreationTokenClassificationRecord as _CreationTokenClassificationRecord,
)
from rubrix.server.services.tasks.token_classification.model import (
    TokenClassificationAggregations as _TokenClassificationAggregations,
)
from rubrix.server.services.tasks.token_classification.model import (
    TokenClassificationAnnotation as _TokenClassificationAnnotation,
)
from rubrix.server.services.tasks.token_classification.model import (
    TokenClassificationDatasetDB as _TokenClassificationDatasetDB,
)
from rubrix.server.services.tasks.token_classification.model import (
    TokenClassificationQuery as _TokenClassificationQuery,
)
from rubrix.server.services.tasks.token_classification.model import (
    TokenClassificationRecord as _TokenClassificationRecord,
)
from rubrix.server.services.tasks.token_classification.model import (
    TokenClassificationRecordDB as _TokenClassificationRecordDB,
)
from rubrix.server.services.tasks.token_classification.model import (
    TokenClassificationSearchResults as _TokenClassificationSearchResults,
)


class TokenClassificationAnnotation(_TokenClassificationAnnotation):
    pass


class CreationTokenClassificationRecord(_CreationTokenClassificationRecord):
    pass


class TokenClassificationRecordDB(_TokenClassificationRecordDB):
    pass


class TokenClassificationRecord(_TokenClassificationRecord):
    def extended_fields(self) -> Dict[str, Any]:
        return {
            "raw_text": self.text,  # Maintain results compatibility
        }


class TokenClassificationBulkData(UpdateDatasetRequest):
    """
    API bulk data for text classification

    Attributes:
    -----------

    records: List[TextClassificationRecord]
        The text classification record list

    """

    records: List[CreationTokenClassificationRecord]


class TokenClassificationQuery(_TokenClassificationQuery):
    pass


class TokenClassificationSearchRequest(BaseModel):

    """
    API SearchRequest request

    Attributes:
    -----------

    query: TokenClassificationQuery
        The search query configuration
    sort:
        The sort by order in search results
    """

    query: TokenClassificationQuery = Field(default_factory=TokenClassificationQuery)
    sort: List[SortableField] = Field(default_factory=list)


class TokenClassificationAggregations(_TokenClassificationAggregations):
    pass


class TokenClassificationSearchResults(_TokenClassificationSearchResults):
    pass


class TokenClassificationDatasetDB(_TokenClassificationDatasetDB):
    pass
