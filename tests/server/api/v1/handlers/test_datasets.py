import pytest

from rubrix.server.api.v1.models.commons.task import TaskType
from rubrix.server.api.v1.models.datasets import (
    DatasetsList,
    Text2TextDatasetCreate,
    TextClassificationDatasetCreate,
    TokenClassificationDatasetCreate,
)


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


def test_list_datasets(mocked_client, api_endpoint, created_datasets):
    response = mocked_client.get(f"{api_endpoint}")
    assert response.status_code == 200, response.json()
    get_all_datasets = DatasetsList.parse_obj(response.json())

    assert get_all_datasets.total == len(created_datasets)
    for ds, expected_ds in zip(get_all_datasets.data, created_datasets):
        assert ds.dict(), expected_ds
