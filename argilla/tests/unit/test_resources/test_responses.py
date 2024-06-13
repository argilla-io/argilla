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

import uuid

import pytest

from argilla import UserResponse, Response


class TestResponses:
    def test_create_user_response(self):
        user_id = uuid.uuid4()
        response = UserResponse(
            answers=[
                Response(question_name="question", value="answer", user_id=user_id),
                Response(question_name="other-question", value="answer", user_id=user_id),
            ],
        )

        assert response.to_dict() == {
            "values": {
                "question": {"value": "answer"},
                "other-question": {"value": "answer"},
            },
            "status": "draft",
            "user_id": str(user_id),
        }

    def test_create_submitted_user_responses(self):
        user_id = uuid.uuid4()
        response = UserResponse(
            answers=[
                Response(question_name="question", value="answer", user_id=user_id, status="submitted"),
                Response(question_name="other-question", value="answer", user_id=user_id, status="submitted"),
            ],
        )

        assert response.to_dict() == {
            "values": {
                "question": {"value": "answer"},
                "other-question": {"value": "answer"},
            },
            "status": "submitted",
            "user_id": str(user_id),
        }

    def test_create_user_response_with_multiple_status(self):
        user_id = uuid.uuid4()
        response = UserResponse(
            answers=[
                Response(question_name="question", value="answer", user_id=user_id, status="draft"),
                Response(question_name="other-question", value="answer", user_id=user_id, status="submitted"),
            ],
        )

        assert response.to_dict() == {
            "values": {
                "question": {"value": "answer"},
                "other-question": {"value": "answer"},
            },
            "status": "draft",
            "user_id": str(user_id),
        }

    def test_create_user_response_with_multiple_user_id(self):
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        with pytest.raises(ValueError, match="Multiple user_ids found in user answers"):
            UserResponse(
                answers=[
                    Response(question_name="question", value="answer", user_id=user_id),
                    Response(question_name="other-question", value="answer", user_id=other_user_id),
                ],
            )
