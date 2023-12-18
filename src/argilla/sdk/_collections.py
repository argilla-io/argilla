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

from typing import TYPE_CHECKING, List

from argilla.sdk import _api as api
from argilla.sdk import _models as models

if TYPE_CHECKING:
    from argilla.sdk._datasets import Dataset


class FieldsCollection:
    def __init__(self, dataset: "Dataset"):
        self.dataset = dataset

    def list(self) -> List[api.Field]:
        return api.Field.list(self.dataset.id)

    def create(self, field: models.Field) -> api.Field:
        return api.Field.create(
            self.dataset.id,
            field.name,
            field.title,
            required=field.required,
            settings=field.settings,
        )

    def __getitem__(self, key: str) -> api.Field:
        return api.Field.by_name(self.dataset.id, name=key)


class QuestionsCollection:
    def __init__(self, dataset: "Dataset"):
        self.dataset = dataset

    def list(self) -> List[api.Question]:
        return api.Question.list(self.dataset.id)

    def create(self, question: models.Question) -> api.Question:
        return api.Question.create(
            self.dataset.id,
            question.name,
            question.title,
            description=question.description,
            required=question.required,
            settings=question.settings,
        )

    def __getitem__(self, key: str) -> api.Question:
        return api.Question.by_name(self.dataset.id, name=key)


