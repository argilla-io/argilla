import pytest

from rubrix.server.commons.errors import MissingDatasetRecordsError
from rubrix.server.commons.es_wrapper import ElasticsearchWrapper, IndexNotFoundError
from rubrix.server.datasets.model import DatasetDB
from rubrix.server.tasks.commons import TaskType
from rubrix.server.tasks.commons.dao.dao import DatasetRecordsDAO


def test_raise_proper_error():
    dao = DatasetRecordsDAO.get_instance(ElasticsearchWrapper.get_instance())
    with pytest.raises(MissingDatasetRecordsError):
        dao.search_records(
            dataset=DatasetDB(name="mock-notfound", task=TaskType.text_classification)
        )
