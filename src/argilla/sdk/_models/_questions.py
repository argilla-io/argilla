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
from typing import Optional
from uuid import UUID

from argilla.sdk._api import *

__all__ = ["Question", "QuestionSettings", "RatingQuestionSettings", "LabelQuestionSettings"]


@dataclasses.dataclass
class Question:
    name: str
    title: str
    settings: QuestionSettings
    description: Optional[str] = None
    required: bool = True

    id: Optional[UUID] = None

    def validate(self):
        pass

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "required": self.required,
            "settings": self.settings.to_dict(),
        }
