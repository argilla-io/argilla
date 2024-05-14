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

import pytest
from argilla_server.apis.v0.models.commons.model import ScoreRange
from argilla_server.apis.v0.models.text_classification import TextClassificationQuery
from argilla_server.daos.backend.search.model import (
    SortableField,
    SortConfig,
    SortOrder,
)
from argilla_server.daos.backend.search.query_builder import EsQueryBuilder


@pytest.mark.parametrize(
    ["index_schema", "sort_cfg", "expected_sort"],
    [
        (
            {
                "mappings": {
                    "properties": {
                        "id": {"type": "text"},
                    }
                }
            },
            [SortableField(id="id")],
            [{"id.keyword": {"order": SortOrder.asc}}],
        ),
        (
            {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                    }
                }
            },
            [SortableField(id="id")],
            [{"id": {"order": SortOrder.asc}}],
        ),
        (
            {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                    }
                }
            },
            [SortableField(id="metadata.black", order=SortOrder.desc)],
            [{"metadata.black": {"order": SortOrder.desc}}],
        ),
    ],
)
def test_build_sort_configuration(index_schema, sort_cfg, expected_sort):
    builder = EsQueryBuilder()

    es_sort = builder.map_2_es_sort_configuration(sort=SortConfig(sort_by=sort_cfg), schema=index_schema)
    assert es_sort == expected_sort


def test_build_sort_with_wrong_field_name():
    builder = EsQueryBuilder()

    index_schema = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
            }
        }
    }

    with pytest.raises(Exception):
        builder.map_2_es_sort_configuration(schema=index_schema, sort=SortConfig(sort_by=[SortableField(id="wat?!")]))


def test_build_sort_without_sort_config():
    builder = EsQueryBuilder()
    index_schema = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
            }
        }
    }
    assert builder.map_2_es_sort_configuration(sort=SortConfig(), schema=index_schema) is None


def test_query_builder_with_query_range():
    es_query = EsQueryBuilder().map_2_es_query(
        schema=None,
        query=TextClassificationQuery(score=ScoreRange(range_from=10)),
    )
    assert es_query == {
        "query": {
            "bool": {
                "filter": {
                    "bool": {
                        "minimum_should_match": 1,
                        "should": [{"range": {"score": {"gte": 10.0}}}],
                    }
                },
                "must": {"match_all": {}},
            }
        }
    }
