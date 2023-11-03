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

from pydantic import BaseModel


class VectorSettings(BaseModel):
    """Schema for the `FeedbackDataset` vectors settings. The vectors setttings are used
    to define the configuration of the vectors associated to the records of a `FeedbackDataset`
    that will be used to perform the vector search.

    Args:
        name: The name of the vector settings.
        title: The title of the vector settings.
        dimensions: The dimensions of the vectors associated with the vector settings.

    Examples:
        >>> from argilla.client.feedback.schemas import VectorSettings
        >>> VectorSettings(name="my_vector_settings", dimensions=768)
    """

    name: str
    title: Optional[str] = None
    dimensions: int
