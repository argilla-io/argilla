# TODO: This license is not consistent with the license used in the project.
#       Delete the inconsistent license and above line and rerun pre-commit to insert a good license.
# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# We skip the flake8 check because we are importing all the models and the import order is important
# flake8: noqa
from argilla_sdk._models._resource import ResourceModel
from argilla_sdk._models._workspace import WorkspaceModel
from argilla_sdk._models._user import UserModel, Role
from argilla_sdk._models._dataset import DatasetModel
from argilla_sdk._models._record._record import RecordModel
from argilla_sdk._models._record._suggestion import SuggestionModel
from argilla_sdk._models._record._response import UserResponseModel, ResponseStatus
from argilla_sdk._models._record._vector import VectorModel
from argilla_sdk._models._record._metadata import MetadataModel, MetadataValue
from argilla_sdk._models._search import (
    SearchQueryModel,
    AndFilterModel,
    FilterModel,
    RangeFilterModel,
    TermsFilterModel,
    ScopeModel,
)
from argilla_sdk._models._settings._fields import (
    TextFieldModel,
    FieldSettings,
    FieldBaseModel,
    FieldModel,
)
from argilla_sdk._models._settings._questions import (
    LabelQuestionModel,
    LabelQuestionSettings,
    MultiLabelQuestionModel,
    QuestionBaseModel,
    QuestionModel,
    QuestionSettings,
    RankingQuestionModel,
    RatingQuestionModel,
    SpanQuestionModel,
    SpanQuestionSettings,
    TextQuestionModel,
    TextQuestionSettings,
)
from argilla_sdk._models._settings._metadata import (
    MetadataFieldModel,
    MetadataPropertyType,
    BaseMetadataPropertySettings,
    TermsMetadataPropertySettings,
    NumericMetadataPropertySettings,
    FloatMetadataPropertySettings,
    IntegerMetadataPropertySettings,
)
from argilla_sdk._models._settings._vectors import VectorFieldModel
