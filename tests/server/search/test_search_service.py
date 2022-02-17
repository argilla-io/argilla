import pytest

import rubrix
from rubrix.server.commons.es_wrapper import ElasticsearchWrapper
from rubrix.server.datasets.model import Dataset
from rubrix.server.tasks.commons import TaskType
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO
from rubrix.server.tasks.commons.metrics.service import MetricsService
from rubrix.server.tasks.search.model import SortConfig
from rubrix.server.tasks.search.query_builder import EsQueryBuilder
from rubrix.server.tasks.search.service import SearchRecordsService
from rubrix.server.tasks.text_classification import (
    TextClassificationQuery,
    TextClassificationRecord,
)


@pytest.fixture
def es_wrapper():
    return ElasticsearchWrapper.get_instance()


@pytest.fixture
def dao(es_wrapper: ElasticsearchWrapper):
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


def test_failing_metrics(service, mocked_client):
    dataset = Dataset(name="test_failing_metrics", task=TaskType.text_classification)

    rubrix.delete(dataset.name)
    rubrix.log(
        rubrix.TextClassificationRecord(inputs="This is a text, yeah!"),
        name=dataset.name,
    )
    results = service.search(
        dataset=dataset,
        query=TextClassificationQuery(),
        sort_config=SortConfig(),
        metrics=["missing-metric"],
        size=0,
        record_type=TextClassificationRecord,
    )

    assert results.dict() == {
        "metrics": {"missing-metric": {}},
        "records": [],
        "total": 1,
    }
