import pytest

import rubrix
from rubrix.server.apis.v0.models.commons.model import ScoreRange, TaskType
from rubrix.server.apis.v0.models.datasets import Dataset
from rubrix.server.apis.v0.models.metrics.base import BaseMetric
from rubrix.server.apis.v0.models.text_classification import (
    TextClassificationQuery,
    TextClassificationRecord,
)
from rubrix.server.apis.v0.models.token_classification import TokenClassificationQuery
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.elasticseach.backend import ElasticsearchBackend
from rubrix.server.elasticseach.search.query_builder import EsQueryBuilder
from rubrix.server.services.metrics import MetricsService
from rubrix.server.services.search.model import SortConfig
from rubrix.server.services.search.service import SearchRecordsService


@pytest.fixture
def es_wrapper():
    return ElasticsearchBackend.get_instance()


@pytest.fixture
def dao(es_wrapper: ElasticsearchBackend):
    return DatasetRecordsDAO.get_instance(es=es_wrapper)


@pytest.fixture
def query_builder(dao: DatasetRecordsDAO):
    return EsQueryBuilder.get_instance(dao=dao)


@pytest.fixture
def metrics(dao: DatasetRecordsDAO, query_builder: EsQueryBuilder):
    return MetricsService.get_instance(dao=dao, query_builder=query_builder)


@pytest.fixture
def service(
    dao: DatasetRecordsDAO, metrics: MetricsService, query_builder: EsQueryBuilder
):
    return SearchRecordsService.get_instance(
        dao=dao, metrics=metrics, query_builder=query_builder
    )


def test_query_builder_with_query_range(query_builder):
    es_query = query_builder(
        "ds", query=TextClassificationQuery(score=ScoreRange(range_from=10))
    )
    assert es_query == {
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


def test_query_builder_with_nested(query_builder, mocked_client):
    dataset = Dataset(
        name="test_query_builder_with_nested",
        owner=rubrix.get_workspace(),
        task=TaskType.token_classification,
    )
    rubrix.delete(dataset.name)
    rubrix.log(
        name=dataset.name,
        records=rubrix.TokenClassificationRecord(
            text="Michael is a professor at Harvard",
            tokens=["Michael", "is", "a", "professor", "at", "Harvard"],
            prediction=[("NAME", 0, 7, 0.9), ("LOC", 26, 33, 0.12)],
        ),
    )

    es_query = query_builder(
        dataset=dataset,
        query=TokenClassificationQuery(
            advanced_query_dsl=True,
            query_text="metrics.predicted.mentions:(label:NAME AND score:[* TO 0.1])",
        ),
    )

    assert es_query == {
        "bool": {
            "filter": {"bool": {"must": {"match_all": {}}}},
            "must": {
                "nested": {
                    "path": "metrics.predicted.mentions",
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "term": {
                                        "metrics.predicted.mentions.label": {
                                            "value": "NAME"
                                        }
                                    }
                                },
                                {
                                    "range": {
                                        "metrics.predicted.mentions.score": {
                                            "lte": "0.1"
                                        }
                                    }
                                },
                            ]
                        }
                    },
                }
            },
        }
    }


def test_failing_metrics(service, mocked_client):

    dataset = Dataset(
        name="test_failing_metrics",
        owner=rubrix.get_workspace(),
        task=TaskType.text_classification,
    )

    rubrix.delete(dataset.name)
    rubrix.log(
        rubrix.TextClassificationRecord(inputs="This is a text, yeah!"),
        name=dataset.name,
    )
    results = service.search(
        dataset=dataset,
        query=TextClassificationQuery(),
        sort_config=SortConfig(),
        metrics=[BaseMetric(id="missing-metric", name="Missing metric")],
        size=0,
        record_type=TextClassificationRecord,
    )

    assert results.dict() == {
        "metrics": {"missing-metric": {}},
        "records": [],
        "total": 1,
    }
