import pytest

from rubrix.server.apis.v0.models.commons.model import TaskType
from rubrix.server.apis.v0.models.datasets import DatasetDB
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.elasticseach.backend import ElasticsearchBackend
from rubrix.server.errors import MissingDatasetRecordsError


def test_raise_proper_error():
    dao = DatasetRecordsDAO.get_instance(ElasticsearchBackend.get_instance())
    with pytest.raises(MissingDatasetRecordsError):
        dao.search_records(
            dataset=DatasetDB(name="mock-notfound", task=TaskType.text_classification)
        )
