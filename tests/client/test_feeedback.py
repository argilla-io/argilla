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

import pytest
from argilla.client import api

if TYPE_CHECKING:
    from argilla.client.feedback import FieldSchema, QuestionSchema

from argilla.client.feedback import (
    FeedbackDataset,
    FeedbackRecord,
    RatingQuestion,
    TextField,
    TextQuestion,
)


class TestFeedbackDataset:
    @pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_fields", "feedback_dataset_questions")
    def test_init(
        self, feedback_dataset_guidelines: str, feedback_dataset_fields: list, feedback_dataset_questions: list
    ) -> None:
        dataset = FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )

        assert dataset.guidelines == feedback_dataset_guidelines
        assert dataset.fields == feedback_dataset_fields
        assert dataset.questions == feedback_dataset_questions

    @pytest.mark.usefixtures("feedback_dataset_fields", "feedback_dataset_questions")
    def test_init_wrong_guidelines(self, feedback_dataset_fields: list, feedback_dataset_questions: list) -> None:
        with pytest.raises(TypeError, match="Expected `guidelines` to be a string"):
            FeedbackDataset(
                guidelines=None,
                fields=feedback_dataset_fields,
                questions=feedback_dataset_questions,
            )

    @pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_questions")
    def test_init_wrong_fields(self, feedback_dataset_guidelines: str, feedback_dataset_questions: list) -> None:
        with pytest.raises(TypeError, match="Expected `fields` to be a list"):
            FeedbackDataset(
                guidelines=feedback_dataset_guidelines,
                fields=None,
                questions=feedback_dataset_questions,
            )
        with pytest.raises(TypeError, match="Expected `fields` to be a list of `FieldSchema`"):
            FeedbackDataset(
                guidelines=feedback_dataset_guidelines,
                fields=[{"wrong": "field"}],
                questions=feedback_dataset_questions,
            )
        with pytest.raises(ValueError, match="At least one `FieldSchema` in `fields` must be required"):
            FeedbackDataset(
                guidelines=feedback_dataset_guidelines,
                fields=[TextField(name="test", required=False)],
                questions=feedback_dataset_questions,
            )

    @pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_fields")
    def test_init_wrong_questions(self, feedback_dataset_guidelines: str, feedback_dataset_fields: list) -> None:
        with pytest.raises(TypeError, match="Expected `questions` to be a list"):
            FeedbackDataset(
                guidelines=feedback_dataset_guidelines,
                fields=feedback_dataset_fields,
                questions=None,
            )
        with pytest.raises(TypeError, match="Expected `questions` to be a list of `QuestionSchema`"):
            FeedbackDataset(
                guidelines=feedback_dataset_guidelines,
                fields=feedback_dataset_fields,
                questions=[{"wrong": "question"}],
            )
        with pytest.raises(ValueError, match="At least one `QuestionSchema` in `questions` must be required"):
            FeedbackDataset(
                guidelines=feedback_dataset_guidelines,
                fields=feedback_dataset_fields,
                questions=[
                    TextQuestion(name="test", required=False),
                    RatingQuestion(name="test", values=[0, 1], required=False),
                ],
            )

    @pytest.mark.usefixtures("feedback_dataset_guidelines", "feedback_dataset_fields", "feedback_dataset_questions")
    def test_records(
        self,
        feedback_dataset_guidelines: str,
        feedback_dataset_fields: List["FieldSchema"],
        feedback_dataset_questions: List["QuestionSchema"],
    ) -> None:
        dataset = FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )

        assert dataset.records == []

        dataset.add_records(
            [
                FeedbackRecord(
                    fields={
                        "text": "A",
                        "label": "B",
                    },
                ),
            ]
        )

        assert len(dataset.records) == 1
        assert dataset.records[0]["fields"] == {
            "text": "A",
            "label": "B",
        }
        assert dataset.records[0]["responses"] == []

        dataset.add_records(
            [
                FeedbackRecord(
                    fields={
                        "text": "C",
                        "label": "D",
                    },
                    responses={
                        "values": {
                            "question-1": {"value": "answer"},
                            "question-2": {"value": 0},
                        },
                        "status": "submitted",
                    },
                    external_id="test-id",
                ),
            ]
        )

        assert len(dataset.records) == 2
        assert dataset.records[1]["fields"] == {
            "text": "C",
            "label": "D",
        }
        assert dataset.records[1]["responses"] == [
            {
                "values": {
                    "question-1": {"value": "answer"},
                    "question-2": {"value": 0},
                },
                "status": "submitted",
            },
        ]

        with pytest.raises(ValueError, match="`rg.FeedbackRecord.fields` does not match the expected schema"):
            dataset.add_records(
                [
                    FeedbackRecord(
                        fields={
                            "wrong": "field",
                        },
                    ),
                ]
            )

        for record in dataset.records:
            assert all(
                key in ["id", "fields", "external_id", "responses", "inserted_at", "updated_at"]
                for key in list(record.keys())
            )

        for batch in dataset.iter(batch_size=1):
            assert len(batch) == 1
            for record in batch:
                assert all(
                    key in ["id", "fields", "external_id", "responses", "inserted_at", "updated_at"]
                    for key in list(record.keys())
                )

        assert len(dataset[:2]) == 2
        assert len(dataset[1:2]) == 1
        assert len(dataset) == len(dataset.records)

    @pytest.mark.usefixtures(
        "feedback_dataset_guidelines",
        "feedback_dataset_fields",
        "feedback_dataset_questions",
        "feedback_dataset_records",
    )
    def test_push_to_argilla_and_from_argilla(
        self,
        mocked_client,
        feedback_dataset_guidelines: str,
        feedback_dataset_fields: List["FieldSchema"],
        feedback_dataset_questions: List["QuestionSchema"],
        feedback_dataset_records: List[FeedbackRecord],
    ) -> None:
        api.active_api()
        api.init(api_key="argilla.apikey")

        dataset = FeedbackDataset(
            guidelines=feedback_dataset_guidelines,
            fields=feedback_dataset_fields,
            questions=feedback_dataset_questions,
        )
        dataset.add_records(records=feedback_dataset_records)
        dataset.push_to_argilla(name="test-dataset")

        assert dataset.argilla_id is not None

        dataset_from_argilla = FeedbackDataset.from_argilla(dataset.argilla_id)

        assert dataset_from_argilla.guidelines == dataset.guidelines
        assert dataset_from_argilla.fields == dataset.fields
        assert dataset_from_argilla.questions == dataset.questions

        assert len(dataset_from_argilla.records) == len(dataset.records)
