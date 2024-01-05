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

from typing import Union

from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla.client.feedback.schemas.remote.fields import RemoteTextField
from argilla.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)
from argilla.client.feedback.schemas.remote.questions import (
    RemoteLabelQuestion,
    RemoteMultiLabelQuestion,
    RemoteRankingQuestion,
    RemoteRatingQuestion,
    RemoteTextQuestion,
)
from argilla.client.feedback.schemas.remote.vector_settings import RemoteVectorSettings
from argilla.client.feedback.schemas.vector_settings import VectorSettings

AllowedFieldTypes = TextField
AllowedRemoteFieldTypes = RemoteTextField
AllowedQuestionTypes = Union[TextQuestion, RatingQuestion, LabelQuestion, MultiLabelQuestion, RankingQuestion]
AllowedRemoteQuestionTypes = Union[
    RemoteTextQuestion, RemoteRatingQuestion, RemoteLabelQuestion, RemoteMultiLabelQuestion, RemoteRankingQuestion
]
AllowedMetadataPropertyTypes = Union[TermsMetadataProperty, FloatMetadataProperty, IntegerMetadataProperty]
AllowedRemoteMetadataPropertyTypes = Union[
    RemoteTermsMetadataProperty, RemoteIntegerMetadataProperty, RemoteFloatMetadataProperty
]
AllowedVectorSettingsTypes = VectorSettings
AllowedRemoteVectorSettingsTypes = RemoteVectorSettings
