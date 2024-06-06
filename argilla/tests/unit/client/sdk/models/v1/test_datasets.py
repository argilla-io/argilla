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

from argilla_server.schemas.v1.datasets import Dataset as ServerSchema
from argilla_server.schemas.v1.questions import Question as ServerQuestionSchema
from argilla_v1.client.sdk.v1.datasets.models import FeedbackDatasetModel as ClientSchema
from argilla_v1.client.sdk.v1.datasets.models import FeedbackQuestionModel as ClientQuestionSchema


def test_feedback_dataset_schema(helpers) -> None:
    assert helpers.are_compatible_api_schemas(ClientSchema.schema(), ServerSchema.schema())


# TODO(alvarobartt): fix schema incompatibility between client and server
# def test_feedback_records_schema(helpers) -> None:
#     assert helpers.are_compatible_api_schemas(ClientRecordsSchema.schema(), ServerRecordsSchema.schema())

# TODO(alvarobartt): fix schema incompatibility between client and server
# def test_feedback_fields_schema(helpers) -> None:
#     assert helpers.are_compatible_api_schemas(ClientFieldSchema.schema(), ServerFieldSchema.schema())


def test_feedback_questions_schema(helpers) -> None:
    assert helpers.are_compatible_api_schemas(ClientQuestionSchema.schema(), ServerQuestionSchema.schema())
