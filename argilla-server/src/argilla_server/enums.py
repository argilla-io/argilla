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


try:
    from enum import StrEnum
except ImportError:
    from argilla_server.utils.str_enum import StrEnum


class FieldType(StrEnum):
    text = "text"
    image = "image"
    chat = "chat"
    custom = "custom"


class ResponseStatus(StrEnum):
    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"


class ResponseStatusFilter(StrEnum):
    draft = "draft"
    pending = "pending"
    submitted = "submitted"
    discarded = "discarded"


class SuggestionType(StrEnum):
    model = "model"
    human = "human"


class DatasetStatus(StrEnum):
    draft = "draft"
    ready = "ready"


class DatasetDistributionStrategy(StrEnum):
    overlap = "overlap"


class UserRole(StrEnum):
    owner = "owner"
    admin = "admin"
    annotator = "annotator"


class RecordStatus(StrEnum):
    pending = "pending"
    completed = "completed"


class RecordInclude(StrEnum):
    responses = "responses"
    suggestions = "suggestions"
    vectors = "vectors"


class QuestionType(StrEnum):
    text = "text"
    rating = "rating"
    label_selection = "label_selection"
    multi_label_selection = "multi_label_selection"
    ranking = "ranking"
    span = "span"


class MetadataPropertyType(StrEnum):
    terms = "terms"  # Textual types with a fixed value list
    integer = "integer"  # Integer values
    float = "float"  # Decimal values


class RecordSortField(StrEnum):
    id = "id"
    external_id = "external_id"
    inserted_at = "inserted_at"
    updated_at = "updated_at"
    status = "status"


class SortOrder(StrEnum):
    asc = "asc"
    desc = "desc"


class SimilarityOrder(StrEnum):
    most_similar = "most_similar"
    least_similar = "least_similar"


class OptionsOrder(StrEnum):
    natural = "natural"
    suggestion = "suggestion"
