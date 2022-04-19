from typing import List

import pytest

from rubrix.server.api.v1.models.commons.task import TaskType
from rubrix.server.api.v1.models.datasets import (
    DatasetsList,
    Text2TextDatasetCreate,
    TextClassificationDatasetCreate,
    TokenClassificationDatasetCreate,
)


@pytest.fixture
def defined_tasks() -> List[TaskType]:
    return [
        TaskType.text_classification,
        TaskType.token_classification,
        TaskType.text2text,
    ]


@pytest.fixture
def clear_all_datasets(mocked_client, api_endpoint):
    response = mocked_client.get(f"{api_endpoint}")
    all_datasets = response.json()
    for ds in all_datasets["data"]:
        mocked_client.delete(f"{api_endpoint}/{ds['task']}/{ds['name']}")


@pytest.fixture
def created_datasets(mocked_client, api_endpoint, clear_all_datasets):

    datasets = []
    for idx, (task, data) in enumerate(
        [
            (
                TaskType.text_classification,
                {
                    "settings": {
                        "multi_label": False,
                        "allowed_labels": ["A", "AA"],
                    },
                },
            ),
            (
                TaskType.text_classification,
                {
                    "settings": {
                        "multi_label": True,
                        "allowed_labels": ["A", "B", "C"],
                    },
                },
            ),
            (
                TaskType.token_classification,
                {},
            ),
            (
                TaskType.text2text,
                {},
            ),
        ]
    ):
        name = f"{task}_dataset_{idx}"
        mocked_client.post(f"{api_endpoint}/{task}", json={"name": name, **data})
        datasets.append(mocked_client.get(f"{api_endpoint}/{task}/{name}").json())
    return datasets


@pytest.fixture
def dataset_name():
    return "dataset4datasets_tests"


@pytest.fixture
def api_endpoint():
    return "/api/v1/datasets"


@pytest.mark.parametrize(
    ("task", "creation_class", "input_data"),
    [
        (
            TaskType.text_classification,
            TextClassificationDatasetCreate,
            {
                "tags": {"a": "tag"},
                "metadata": {"a": "metadata"},
                "settings": {"multi_label": True, "allowed_labels": ["A", "B", "C"]},
            },
        ),
        (
            TaskType.token_classification,
            TokenClassificationDatasetCreate,
            {
                "tags": {"token": "tag"},
                "metadata": {"token": "metadata"},
            },
        ),
        (
            TaskType.text2text,
            Text2TextDatasetCreate,
            {
                "tags": {"text2text": "tag"},
                "metadata": {"text2text": "metadata"},
            },
        ),
    ],
)
def test_create_dataset(
    mocked_client, api_endpoint, dataset_name, task, creation_class, input_data
):
    def dataset_validation(response):
        assert response.status_code == 200, response.json()
        output_response = response.json()
        for exclude_field in ["created_at", "last_updated"]:
            assert output_response.pop(exclude_field)
        assert output_response == {
            "owner": "rubrix",
            "created_by": "rubrix",
            "task": task,
            **data,
        }

    dataset = dataset_name
    if mocked_client.get(f"{api_endpoint}/{task}/{dataset}").status_code == 200:
        response = mocked_client.delete(f"{api_endpoint}/{task}/{dataset}")
        assert response.status_code == 200, response.json()

    data = creation_class.parse_obj({"name": dataset, **input_data}).dict()
    response = mocked_client.post(
        f"{api_endpoint}/{task}",
        json=data,
    )
    dataset_validation(response)
    dataset_validation(mocked_client.get(f"{api_endpoint}/{task}/{dataset}"))


def test_list_datasets(mocked_client, api_endpoint, created_datasets, defined_tasks):
    def validate_datasets(datasets, expected_datasets):
        for ds in datasets:
            ds_was_found = False
            for created_ds in expected_datasets:
                if ds.name == created_ds["name"]:
                    ds_was_found = True
                    assert ds == ds.__class__.parse_obj(created_ds)
            assert ds_was_found, ds

    response = mocked_client.get(f"{api_endpoint}")
    assert response.status_code == 200, response.json()
    get_all_datasets = DatasetsList.parse_obj(response.json())

    assert get_all_datasets.total == len(created_datasets)
    validate_datasets(get_all_datasets.data, created_datasets)

    for task in defined_tasks:
        datasets_by_task = [ds for ds in created_datasets if ds["task"] == task]
        response = mocked_client.get(f"{api_endpoint}/{task}")

        assert response.status_code == 200, response.json()
        get_task_datasets = DatasetsList.parse_obj(response.json())
        assert get_task_datasets.total == len(datasets_by_task)
        validate_datasets(get_task_datasets.data, datasets_by_task)


def test_open_and_close_datasets(mocked_client, api_endpoint, created_datasets):
    for dataset in created_datasets:
        task, name = dataset["task"], dataset["name"]
        # Opening a dataset for an already opened ds has no effect
        response = mocked_client.post(f"{api_endpoint}/{task}/{name}:open")
        assert response.status_code == 200, response.json()
        # Closing a dataset will stop searches, metrics and weak supervision actions
        response = mocked_client.post(f"{api_endpoint}/{task}/{name}:close")
        assert response.status_code == 200, response.json()
        # TODO: check that dataset cannot be explorable
        # Nothing happens when closing a closed dataset
        response = mocked_client.post(f"{api_endpoint}/{task}/{name}:close")
        assert response.status_code == 200, response.json()
        # We recover searches after reopen the dataset
        response = mocked_client.post(f"{api_endpoint}/{task}/{name}:open")
        assert response.status_code == 200, response.json()
        # TODO: check that dataset cannot be explorable


def test_delete_datasets(mocked_client, api_endpoint, created_datasets):
    for dataset in created_datasets:
        task, name = dataset["task"], dataset["name"]
        response = mocked_client.delete(f"{api_endpoint}/{task}/{name}")
        assert response.status_code == 200, response.json()
        response = mocked_client.get(f"{api_endpoint}/{task}/{name}")
        assert response.status_code == 404, response.json()


def test_update_datasets(mocked_client, api_endpoint, created_datasets):
    for dataset in created_datasets:
        task, name = dataset["task"], dataset["name"]

        current_tags = dataset["tags"]
        current_metadata = dataset["metadata"]
        response = mocked_client.patch(
            f"{api_endpoint}/{task}/{name}",
            json={"tags": {"This": "is"}, "metadata": {"an": "update"}},
        )
        assert response.status_code == 200, response.json()
        updated_dataset = response.json()

        response = mocked_client.get(f"{api_endpoint}/{task}/{name}")
        assert response.status_code == 200, response.json()
        assert updated_dataset == response.json()

        assert current_tags != updated_dataset["tags"]
        assert current_metadata != updated_dataset["metadata"]


def test_copy_datasets(mocked_client, api_endpoint, created_datasets, defined_tasks):
    for dataset in created_datasets:
        task, name = dataset["task"], dataset["name"]
        new_dataset_name = f"{name}_copy"
        response = mocked_client.post(
            f"{api_endpoint}/{task}/{name}:copy",
            json={
                "name": new_dataset_name,
                "tags": {"This": "is"},
                "metadata": {"a": "copy"},
            },
        )
        assert response.status_code == 200, response.json()
        copied_dataset = response.json()
        response = mocked_client.get(f"{api_endpoint}/{task}/{name}")
        assert response.status_code == 200, response.json()
        assert copied_dataset == response.json()
