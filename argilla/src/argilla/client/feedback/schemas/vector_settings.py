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

from typing import Optional

from argilla.client.feedback.schemas.validators import title_must_have_value
from argilla.pydantic_v1 import BaseModel, Field, PositiveInt, validator


class VectorSettings(BaseModel):
    """Schema for the `FeedbackDataset` vectors settings. The vectors setttings are used
    to define the configuration of the vectors associated to the records of a `FeedbackDataset`
    that will be used to perform the vector search.

    Args:
        name: The name of the vector settings.
        title: The title of the vector settings. If not provided, it will be capitalized
            from the `name` field. And its what will be shown in the UI. Defaults to
            `None`.
        dimensions: The dimensions of the vectors associated with the vector settings.

    Examples:
        >>> from argilla.client.feedback.schemas import VectorSettings
        >>> VectorSettings(name="my_vector_settings", dimensions=768)
    """

    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    title: Optional[str] = None
    dimensions: PositiveInt

    _title_must_have_value = validator("title", always=True, allow_reuse=True)(title_must_have_value)
