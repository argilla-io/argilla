from time import sleep

from rubrix.server.commons.es_wrapper import create_es_wrapper
from rubrix.server.commons.models import TaskType
from rubrix.server.datasets.dao import create_datasets_dao
from rubrix.server.datasets.model import DatasetDB

es_wrapper = create_es_wrapper()
dao = create_datasets_dao(es_wrapper)


def test_retrieve_ownered_dataset_for_no_owner_user():
    dataset = "test_retrieve_ownered_dataset_for_no_owner_user"
    created = dao.create_dataset(
        DatasetDB(
            name=dataset, owner="other", task=TaskType.text_classification
        )
    )
    assert dao.find_by_name(created.name, owner=created.owner) == created
    assert dao.find_by_name(created.name, owner=None) == created
    assert dao.find_by_name(created.name, owner="me") == created
