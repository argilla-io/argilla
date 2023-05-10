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

import random

import pytest
from argilla.server.elasticsearch import ElasticSearchEngine
from elasticsearch8 import BadRequestError, Elasticsearch
from sqlalchemy.orm import Session

from tests.conftest import is_running_elasticsearch
from tests.factories import (
    DatasetFactory,
    RatingQuestionFactory,
    TextQuestionFactory,
)


@pytest.mark.asyncio
@pytest.mark.skipif(condition=not is_running_elasticsearch(), reason="Test only running with elasticsearch backend")
class TestSuiteElasticSearchEngine:
    async def test_create_index_for_dataset(self, search_engine: ElasticSearchEngine, elasticsearch: Elasticsearch):
        dataset = DatasetFactory.create()
        await search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert elasticsearch.indices.exists(index=index_name)

        index = elasticsearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "dynamic_templates": [],
            "properties": {
                "fields": {"dynamic": "true", "type": "object"},
                "responses": {"dynamic": "true", "type": "object"},
            },
        }

    @pytest.mark.parametrize(
        argnames=("text_ann_size", "rating_ann_size"),
        argvalues=[(random.randint(1, 9), random.randint(1, 9)) for _ in range(1, 5)],
    )
    async def test_create_index_for_dataset_with_questions(
        self,
        search_engine: ElasticSearchEngine,
        elasticsearch: Elasticsearch,
        db: Session,
        text_ann_size: int,
        rating_ann_size: int,
    ):
        text_questions = TextQuestionFactory.create_batch(size=text_ann_size)
        rating_questions = RatingQuestionFactory.create_batch(size=rating_ann_size)

        dataset = DatasetFactory.create(questions=text_questions + rating_questions)

        await search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert elasticsearch.indices.exists(index=index_name)

        index = elasticsearch.indices.get(index=index_name)[index_name]
        assert index["mappings"] == {
            "dynamic": "strict",
            "properties": {
                "fields": {"dynamic": "true", "type": "object"},
                "responses": {"dynamic": "true", "type": "object"},
            },
            "dynamic_templates": [
                *[
                    config
                    for question in text_questions
                    for config in [
                        {
                            f"{question.name}_responses": {
                                "mapping": {"type": "text"},
                                "path_match": f"responses.*.{question.name}",
                            }
                        },
                    ]
                ],
                *[
                    config
                    for question in rating_questions
                    for config in [
                        {
                            f"{question.name}_responses": {
                                "mapping": {"type": "integer"},
                                "path_match": f"responses.*.{question.name}",
                            }
                        },
                    ]
                ],
            ],
        }

    async def test_create_index_with_existing_index(
        self, search_engine: ElasticSearchEngine, elasticsearch: Elasticsearch, db: Session
    ):
        dataset = DatasetFactory.create()
        await search_engine.create_index(dataset)

        index_name = f"rg.{dataset.id}"
        assert elasticsearch.indices.exists(index=index_name)

        with pytest.raises(BadRequestError, match="'resource_already_exists_exception', 'index"):
            await search_engine.create_index(dataset)
