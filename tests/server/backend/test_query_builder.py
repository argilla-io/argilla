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

from argilla.server.daos.backend.search.model import (
    SortableField,
    SortConfig,
    SortOrder,
)
from argilla.server.daos.backend.search.query_builder import EsQueryBuilder


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

    es_sort = builder.map_2_es_sort_configuration(
        sort=SortConfig(sort_by=sort_cfg), schema=index_schema
    )
    assert es_sort == expected_sort


def test_build_sort_with_wrong_field_name():
    builder = EsQueryBuilder()

    with pytest.raises(Exception):
        builder.map_2_es_sort_configuration(
            sort=SortConfig(sort_by=[SortableField(id="wat?!")])
        )


def test_build_sort_without_sort_config():
    builder = EsQueryBuilder()
    assert builder.map_2_es_sort_configuration() is None
