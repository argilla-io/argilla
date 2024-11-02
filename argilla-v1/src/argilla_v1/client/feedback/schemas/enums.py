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
from enum import Enum
from typing import List


class FieldTypes(str, Enum):
    text = "text"


class QuestionTypes(str, Enum):
    text = "text"
    rating = "rating"
    label_selection = "label_selection"
    multi_label_selection = "multi_label_selection"
    ranking = "ranking"
    span = "span"

    @classmethod
    def values(cls) -> List[str]:
        return [_type.value for _type in cls]


class MetadataPropertyTypes(str, Enum):
    terms = "terms"
    integer = "integer"
    float = "float"


class RecordSortField(str, Enum):
    inserted_at = "inserted_at"
    updated_at = "updated_at"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class ResponseStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"


class ResponseStatusFilter(str, Enum):
    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"
    pending = "pending"


class LabelsOrder(str, Enum):
    natural = "natural"
    suggestion = "suggestion"
