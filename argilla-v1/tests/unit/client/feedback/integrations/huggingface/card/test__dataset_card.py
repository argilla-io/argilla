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

import json
import re
from typing import TYPE_CHECKING, List
from uuid import uuid4

import pytest
from argilla_v1.client.feedback.integrations.huggingface.card import ArgillaDatasetCard
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.questions import (
    LabelQuestion,
    MultiLabelQuestion,
    RankingQuestion,
    RatingQuestion,
    TextQuestion,
)
from argilla_v1.client.feedback.schemas.records import FeedbackRecord
from argilla_v1.client.feedback.schemas.types import AllowedMetadataPropertyTypes
from argilla_v1.client.feedback.schemas.vector_settings import VectorSettings
from huggingface_hub import DatasetCardData

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas import FeedbackRecord
    from argilla_v1.client.feedback.schemas.types import AllowedFieldTypes, AllowedQuestionTypes


class TestSuiteArgillaDatasetCard:
    @pytest.mark.parametrize(
        "repo_id,fields,questions,guidelines,metadata_properties,vectors_settings,record",
        [
            (
                f"argilla/dataset-card-{uuid4()}",
                [TextField(name="text-field")],
                [
                    TextQuestion(name="text-question"),
                    RatingQuestion(name="rating-question", values=[1, 2, 3]),
                    LabelQuestion(name="label-question", labels=["a", "b", "c"]),
                    MultiLabelQuestion(name="multi-label-question", labels=["a", "b", "c"]),
                    RankingQuestion(name="ranking-question", values=["a", "b", "c"]),
                ],
                "## Guidelines",
                [
                    TermsMetadataProperty(name="color", values=["red", "blue"]),
                    IntegerMetadataProperty(name="day", min=0, max=31, visible_for_annotators=False),
                    FloatMetadataProperty(name="price", min=0, max=100),
                ],
                [VectorSettings(name="float-vector", dimensions=2)],
                FeedbackRecord(
                    fields={"text-field": "text"},
                    responses=[
                        {
                            "values": {
                                "text-question": {"value": "text"},
                                "rating-question": {"value": 1},
                                "label-question": {"value": "a"},
                                "multi-label-question": {"value": ["a", "b"]},
                                "ranking-question": {"value": ["a", "b", "c"]},
                            },
                            "user_id": str(uuid4()),
                            "status": "submitted",
                        },
                    ],
                    suggestions=[
                        {
                            "question_name": "text-question",
                            "value": "text",
                        },
                        {
                            "question_name": "rating-question",
                            "value": 1,
                        },
                        {
                            "question_name": "label-question",
                            "value": "a",
                        },
                        {
                            "question_name": "multi-label-question",
                            "value": ["a", "b"],
                        },
                        {
                            "question_name": "ranking-question",
                            "value": ["a", "b", "c"],
                        },
                    ],
                    vectors={"float-vector": [1.0, 2.0]},
                    external_id="external-id-1",
                ),
            )
        ],
    )
    def test_from_template(
        self,
        repo_id: str,
        fields: List["AllowedFieldTypes"],
        questions: List["AllowedQuestionTypes"],
        guidelines: str,
        vectors_settings: List[VectorSettings],
        record: FeedbackRecord,
        metadata_properties: List[AllowedMetadataPropertyTypes],
    ) -> None:
        card = ArgillaDatasetCard.from_template(
            card_data=DatasetCardData(
                language="en",
                size_categories="n<1K",
                tags=["rlfh", "argilla", "human-feedback"],
            ),
            template_path=ArgillaDatasetCard.default_template_path,
            repo_id=repo_id,
            argilla_fields=fields,
            argilla_questions=questions,
            argilla_guidelines=guidelines,
            argilla_metadata_properties=metadata_properties,
            argilla_vectors_settings=vectors_settings,
            argilla_record=json.loads(record.json()),
            huggingface_record=record.json(),
        )

        assert isinstance(card, ArgillaDatasetCard)
        assert card.default_template_path == ArgillaDatasetCard.default_template_path
        assert card.content.__contains__(f"# Dataset Card for {repo_id.split('/')[1]}")
        assert all(field.name in card.content for field in fields)
        assert all(question.name in card.content for question in questions)
        assert all(vector_settings.name in card.content for vector_settings in vectors_settings)
        assert guidelines in card.content
        assert re.search("\| color \| color \| terms \| \['red', 'blue'\] \| True \|", card.content)
        assert re.search("\| day \| day \| integer \| 0 - 31 \| False \|", card.content)
        assert re.search("\| price \| price \| float \| 0\.0 - 100\.0 \| True \|", card.content)

        # In case we implement new metadata_property types and forget about the poor little dataset cards ...
        for allowed_metadata_type in AllowedMetadataPropertyTypes.__args__:
            if allowed_metadata_type not in [type(metadata) for metadata in metadata_properties]:
                raise NotImplementedError(f"ArgillaDatasetCard not tested for '{allowed_metadata_type}'.")
