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

from uuid import uuid4

import argilla_server.errors.future as errors
import pytest
from argilla_server.api.schemas.v1.records import SearchRecordsQuery
from argilla_server.contexts.search import SearchRecordsQueryValidator
from sqlalchemy.ext.asyncio import AsyncSession

from argilla_server.models import Dataset
from tests.factories import (
    DatasetFactory,
    FloatMetadataPropertyFactory,
    LabelSelectionQuestionFactory,
    TextQuestionFactory,
)


@pytest.mark.asyncio
class TestSearchRecordsQueryValidator:
    async def test_validate(self, db: AsyncSession):
        dataset = await DatasetFactory.create()
        text_question = await TextQuestionFactory.create(dataset=dataset)
        label_selection_question = await LabelSelectionQuestionFactory.create(dataset=dataset)
        metadata_property = await FloatMetadataPropertyFactory.create(dataset=dataset)

        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "filters": {
                    "and": [
                        {
                            "type": "terms",
                            "scope": {"entity": "response", "question": text_question.name, "property": "status"},
                            "values": ["submitted", "draft"],
                        },
                        {
                            "type": "terms",
                            "scope": {"entity": "suggestion", "question": text_question.name, "property": "agent"},
                            "values": ["GPT-3.5", "GPT-4"],
                        },
                        {
                            "type": "terms",
                            "scope": {"entity": "suggestion", "question": label_selection_question.name},
                            "values": ["politics", "news"],
                        },
                        {
                            "type": "range",
                            "scope": {"entity": "suggestion", "question": text_question.name, "property": "score"},
                            "ge": 0.8,
                            "le": 1.0,
                        },
                        {
                            "type": "range",
                            "scope": {"entity": "metadata", "metadata_property": metadata_property.name},
                            "ge": 0.5,
                            "le": 0.8,
                        },
                    ]
                },
                "sort": [
                    {"scope": {"entity": "record", "property": "inserted_at"}, "order": "desc"},
                    {"scope": {"entity": "record", "property": "updated_at"}, "order": "desc"},
                    {
                        "scope": {"entity": "suggestion", "question": text_question.name, "property": "score"},
                        "order": "desc",
                    },
                    {"scope": {"entity": "metadata", "metadata_property": metadata_property.name}, "order": "asc"},
                ],
            }
        )

        await SearchRecordsQueryValidator.validate(db, dataset, query)

    async def test_validate_response_filter_scope_in_filters_without_question(self, db: AsyncSession):
        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "filters": {"and": [{"type": "terms", "scope": {"entity": "response"}, "values": ["value"]}]},
            }
        )

        await SearchRecordsQueryValidator.validate(db, Dataset(id=uuid4()), query)

    async def test_validate_response_filter_scope_in_filters_with_non_existent_question(self, db: AsyncSession):
        dataset = await DatasetFactory.create()

        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "filters": {
                    "and": [
                        {
                            "type": "terms",
                            "scope": {"entity": "response", "question": "non-existent"},
                            "values": ["value"],
                        }
                    ]
                },
            }
        )

        with pytest.raises(errors.NotFoundError) as not_found_error:
            await SearchRecordsQueryValidator.validate(db, dataset, query)

        assert (
            str(not_found_error.value) == f"Question not found filtering by name=non-existent, dataset_id={dataset.id}"
        )

    async def test_validate_suggestion_filter_scope_in_filters_with_non_existent_question(self, db: AsyncSession):
        dataset = await DatasetFactory.create()

        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "filters": {
                    "and": [
                        {
                            "type": "terms",
                            "scope": {"entity": "suggestion", "question": "non-existent"},
                            "values": ["value"],
                        }
                    ]
                },
            }
        )

        with pytest.raises(errors.NotFoundError) as not_found_error:
            await SearchRecordsQueryValidator.validate(db, dataset, query)

        assert (
            str(not_found_error.value) == f"Question not found filtering by name=non-existent, dataset_id={dataset.id}"
        )

    async def test_validate_metadata_filter_scope_in_filters_with_non_existent_metadata_property(
        self, db: AsyncSession
    ):
        dataset = await DatasetFactory.create()

        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "filters": {
                    "and": [
                        {
                            "type": "terms",
                            "scope": {"entity": "metadata", "metadata_property": "non-existent"},
                            "values": ["value"],
                        }
                    ]
                },
            }
        )

        with pytest.raises(errors.NotFoundError) as not_found_error:
            await SearchRecordsQueryValidator.validate(db, dataset, query)

        assert (
            str(not_found_error.value)
            == f"MetadataProperty not found filtering by name=non-existent, dataset_id={dataset.id}"
        )

    async def test_validate_response_filter_scope_in_sort_without_question(self, db: AsyncSession):
        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "sort": [{"scope": {"entity": "response"}, "order": "asc"}],
            }
        )

        await SearchRecordsQueryValidator.validate(db, Dataset(id=uuid4()), query)

    async def test_validate_response_filter_scope_in_sort_with_non_existent_question(self, db: AsyncSession):
        dataset = await DatasetFactory.create()

        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "sort": [{"scope": {"entity": "response", "question": "non-existent"}, "order": "asc"}],
            }
        )

        with pytest.raises(errors.NotFoundError) as not_found_error:
            await SearchRecordsQueryValidator.validate(db, dataset, query)

        assert (
            str(not_found_error.value) == f"Question not found filtering by name=non-existent, dataset_id={dataset.id}"
        )

    async def test_validate_suggestion_filter_scope_in_sort_with_non_existent_question(self, db: AsyncSession):
        dataset = await DatasetFactory.create()

        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "sort": [{"scope": {"entity": "suggestion", "question": "non-existent"}, "order": "asc"}],
            }
        )

        with pytest.raises(errors.NotFoundError) as not_found_error:
            await SearchRecordsQueryValidator.validate(db, dataset, query)

        assert (
            str(not_found_error.value) == f"Question not found filtering by name=non-existent, dataset_id={dataset.id}"
        )

    async def test_validate_metadata_filter_scope_in_sort_with_non_existent_metadata_property(self, db: AsyncSession):
        dataset = await DatasetFactory.create()

        query = SearchRecordsQuery.model_validate(
            {
                "query": {
                    "text": {"q": "query"},
                },
                "sort": [{"scope": {"entity": "metadata", "metadata_property": "non-existent"}, "order": "asc"}],
            }
        )

        with pytest.raises(errors.NotFoundError) as not_found_error:
            await SearchRecordsQueryValidator.validate(db, dataset, query)

        assert (
            str(not_found_error.value)
            == f"MetadataProperty not found filtering by name=non-existent, dataset_id={dataset.id}"
        )
