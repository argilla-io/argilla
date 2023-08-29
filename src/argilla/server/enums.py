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


class FieldType(str, Enum):
    text = "text"


class ResponseStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    discarded = "discarded"


class ResponseStatusFilter(str, Enum):
    draft = "draft"
    missing = "missing"
    submitted = "submitted"
    discarded = "discarded"


class SuggestionType(str, Enum):
    model = "model"
    human = "human"


class DatasetStatus(str, Enum):
    draft = "draft"
    ready = "ready"


class UserRole(str, Enum):
    owner = "owner"
    admin = "admin"
    annotator = "annotator"


class RecordInclude(str, Enum):
    responses = "responses"
    suggestions = "suggestions"


class QuestionType(str, Enum):
    text = "text"
    rating = "rating"
    label_selection = "label_selection"
    multi_label_selection = "multi_label_selection"
    ranking = "ranking"
