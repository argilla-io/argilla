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
from argilla.server.models import AnnotationType
from argilla.server.schemas.v1.records import RecordCreate
from argilla.server.settings import settings
from elasticsearch import BadRequestError, Elasticsearch
from opensearchpy import OpenSearch
from sqlalchemy.orm import Session

from tests.factories import (
    AnnotationFactory,
    DatasetFactory,
    RatingAnnotationFactory,
    TextAnnotationFactory,
)


def _index_name_for_dataset(dataset):
    return f"rg.{dataset.id}"


def _running_with_elasticsearch() -> str:
    open_search = OpenSearch(hosts=settings.elasticsearch)

    info = open_search.info(format="json")
    version_info = info["version"]

    return "distribution" not in version_info


@pytest.fixture(scope="session")
def es_config():
    return {"hosts": settings.elasticsearch}


@pytest.fixture(scope="session")
def elasticsearch(es_config):
    client = Elasticsearch(**es_config)
    yield client

    for index_info in client.cat.indices(index="ar.*,rg.*", format="json"):
        client.indices.delete(index=index_info["index"])


@pytest.fixture(scope="session")
def search_engine(es_config):
    return ElasticSearchEngine(config=es_config)


@pytest.mark.skipif(
    condition=not _running_with_elasticsearch(),
    reason="Test only running with elasticsearch backend",
)
def test_create_index_for_dataset(search_engine: ElasticSearchEngine, elasticsearch: Elasticsearch, db: Session):
    dataset = DatasetFactory.create()
    search_engine.create_index(dataset)

    index_name = f"rg.{dataset.id}"
    assert elasticsearch.indices.exists(index=index_name)

    index = elasticsearch.indices.get(index=index_name)[index_name]
    assert index["mappings"] == {
        "dynamic": "strict",
        "dynamic_templates": [],
        "properties": {
            "fields": {"dynamic": "false", "type": "object"},
            "annotations": {"dynamic": "true", "type": "object"},
            "predictions": {"dynamic": "true", "type": "object"},
            "metadata": {"dynamic": "false", "type": "object"},
            "vectors": {"dynamic": "false", "type": "object"},
        },
    }


@pytest.mark.skipif(
    condition=not _running_with_elasticsearch(),
    reason="Test only running with elasticsearch backend",
)
@pytest.mark.parametrize(
    argnames=("text_ann_size", "rating_ann_size"),
    argvalues=[(random.randint(1, 9), random.randint(1, 9)) for _ in range(1, 5)],
)
def test_create_index_for_dataset_with_annotations(
    search_engine: ElasticSearchEngine,
    elasticsearch: Elasticsearch,
    db: Session,
    text_ann_size: int,
    rating_ann_size: int,
):
    text_annotations = AnnotationFactory.create_batch(size=text_ann_size, type=AnnotationType.text)
    rating_annotations = AnnotationFactory.create_batch(size=rating_ann_size, type=AnnotationType.rating)

    dataset = DatasetFactory.create(annotations=text_annotations + rating_annotations)

    search_engine.create_index(dataset)

    index_name = _index_name_for_dataset(dataset)
    assert elasticsearch.indices.exists(index=index_name)

    index = elasticsearch.indices.get(index=index_name)[index_name]
    assert index["mappings"] == {
        "dynamic": "strict",
        "properties": {
            "fields": {"dynamic": "false", "type": "object"},
            "annotations": {"dynamic": "true", "type": "object"},
            "predictions": {"dynamic": "true", "type": "object"},
            "metadata": {"dynamic": "false", "type": "object"},
            "vectors": {"dynamic": "false", "type": "object"},
        },
        "dynamic_templates": [
            *[
                config
                for annotation in text_annotations
                for config in [
                    {
                        f"{annotation.name}_annotations": {
                            "mapping": {"index": False, "type": "text"},
                            "path_match": f"annotations.*.{annotation.name}.value",
                        }
                    },
                    {
                        f"{annotation.name}_predictions": {
                            "mapping": {"index": False, "type": "text"},
                            "path_match": f"predictions.*.{annotation.name}.value",
                        }
                    },
                ]
            ],
            *[
                config
                for annotation in rating_annotations
                for config in [
                    {
                        f"{annotation.name}_annotations": {
                            "mapping": {"type": "integer"},
                            "path_match": f"annotations.*.{annotation.name}.value",
                        }
                    },
                    {
                        f"{annotation.name}_predictions": {
                            "mapping": {"type": "integer"},
                            "path_match": f"predictions.*.{annotation.name}.value",
                        }
                    },
                ]
            ],
        ],
    }


@pytest.mark.skipif(
    condition=not _running_with_elasticsearch(),
    reason="Test only running with elasticsearch backend",
)
def test_create_index_with_existing_index(
    search_engine: ElasticSearchEngine, elasticsearch: Elasticsearch, db: Session
):
    dataset = DatasetFactory.create()
    search_engine.create_index(dataset)

    index_name = _index_name_for_dataset(dataset)
    assert elasticsearch.indices.exists(index=index_name)

    with pytest.raises(BadRequestError, match="'resource_already_exists_exception', 'index"):
        search_engine.create_index(dataset)


def test_index_records_for_non_existing_index(
    search_engine: ElasticSearchEngine, elasticsearch: Elasticsearch, db: Session
):
    dataset = DatasetFactory.create()

    records = [
        RecordCreate.parse_obj({"fields": {"text": text}, "annotations": {"username": {"is_ok": {"value": True}}}})
        for text in ["this is a text"] * 10
    ]

    with pytest.raises(
        RuntimeError, match=r"Unable to add data batch to Dataset\(.*\)\. The specified index is invalid\."
    ):
        search_engine.add_data_batch(dataset, batch=[r.dict() for r in records])


def test_add_records_to_index(search_engine: ElasticSearchEngine, elasticsearch: Elasticsearch, db: Session):
    dataset = DatasetFactory.create(
        annotations=[TextAnnotationFactory.create(name="notes"), RatingAnnotationFactory.create(name="rating")]
    )

    search_engine.create_index(dataset)

    records = [
        RecordCreate.parse_obj(
            {
                "fields": {"text": text},
                "annotations": {
                    f"username{idx % 3}": {
                        "notes": {"value": "Here my notes"},
                        "rating": {"value": 5},
                    }
                },
            }
        )
        for idx, text in enumerate(["this is a text"] * 10)
    ]

    search_engine.add_data_batch(dataset, batch=[r.dict() for r in records])

    index_name = _index_name_for_dataset(dataset)

    elasticsearch.indices.refresh(index=index_name)
    assert elasticsearch.count(index=index_name, human=True)["count"] == len(records)

    index = elasticsearch.indices.get(index=index_name)[index_name]
    assert index["mappings"]["properties"] == {
        "fields": {"dynamic": "false", "type": "object"},
        "metadata": {"dynamic": "false", "type": "object"},
        "vectors": {"dynamic": "false", "type": "object"},
        "predictions": {"dynamic": "true", "type": "object"},
        "annotations": {
            "dynamic": "true",
            "properties": {
                "username0": {
                    "properties": {
                        "notes": {"properties": {"value": {"index": False, "type": "text"}}},
                        "rating": {"properties": {"value": {"type": "integer"}}},
                    }
                },
                "username1": {
                    "properties": {
                        "notes": {"properties": {"value": {"index": False, "type": "text"}}},
                        "rating": {"properties": {"value": {"type": "integer"}}},
                    }
                },
                "username2": {
                    "properties": {
                        "notes": {"properties": {"value": {"index": False, "type": "text"}}},
                        "rating": {"properties": {"value": {"type": "integer"}}},
                    }
                },
            },
        },
    }
