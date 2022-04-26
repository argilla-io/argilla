from typing import List

import pytest

from rubrix.server.apis.v0.models.datasets import Dataset as DatasetV0
from rubrix.server.apis.v1.models.commons.task import TaskType
from rubrix.server.apis.v1.models.dataset_settings import (
    LabelsSchema,
    TextClassificationSettings,
    TokenClassificationSettings,
)
from rubrix.server.apis.v1.models.datasets import DatasetCreate


@pytest.fixture
def defined_tasks() -> List[TaskType]:
    return [
        TaskType.text_classification,
        TaskType.token_classification,
        TaskType.text2text,
    ]


@pytest.fixture
def clear_all_datasets(mocked_client, old_api_endpoint):
    response = mocked_client.get(f"{old_api_endpoint}/")
    all_datasets = response.json()
    for ds in all_datasets:
        mocked_client.delete(f"{old_api_endpoint}/{ds['name']}")


@pytest.fixture
def dataset_name():
    return "dataset4datasets_tests"


@pytest.fixture
def api_endpoint():
    return "/api/v1/datasets"


@pytest.fixture
def old_api_endpoint():
    return "/api/datasets"


@pytest.mark.parametrize(
    ("task", "input_data"),
    [
        (
            TaskType.text_classification,
            {
                "tags": {"a": "tag"},
                "metadata": {"a": "metadata"},
            },
        ),
        (
            TaskType.token_classification,
            {
                "tags": {"token": "tag"},
                "metadata": {"token": "metadata"},
            },
        ),
        (
            TaskType.text2text,
            {
                "tags": {"text2text": "tag"},
                "metadata": {"text2text": "metadata"},
            },
        ),
    ],
)
def test_create_dataset(
    mocked_client,
    api_endpoint,
    old_api_endpoint,
    clear_all_datasets,
    dataset_name,
    task,
    input_data,
):
    def dataset_validation(response, expected):
        assert response.status_code == 200, response.json()
        output_response = response.json()
        for exclude_field in ["created_at", "last_updated"]:
            assert output_response.pop(exclude_field)
        assert output_response == expected

    dataset = dataset_name
    data = DatasetCreate.parse_obj({"name": dataset, **input_data}).dict()
    response = mocked_client.post(
        f"{api_endpoint}/{task}",
        json=data,
    )
    dataset_validation(
        response,
        expected={
            "owner": "rubrix",
            "created_by": "rubrix",
            "task": task,
            **data,
        },
    )
    dataset_validation(
        mocked_client.get(f"{old_api_endpoint}/{dataset}"),
        expected={
            "owner": "rubrix",
            "task": task.as_old_task_type(),
            **data,
        },
    )


@pytest.mark.parametrize(
    ("task", "settings"),
    [
        (
            TaskType.text_classification,
            TextClassificationSettings(
                labels_schema=LabelsSchema(
                    labels=[
                        LabelsSchema.Schema(id="A", name="A"),
                        LabelsSchema.Schema(id="B", name="B"),
                        LabelsSchema.Schema(id="C", name="C"),
                    ]
                )
            ),
        ),
        (
            TaskType.token_classification,
            TokenClassificationSettings(
                labels_schema=LabelsSchema(
                    labels=[
                        LabelsSchema.Schema(id="PER", name="PERSON"),
                        LabelsSchema.Schema(id="ORG", name="ORGANIZATION"),
                    ]
                )
            ),
        ),
    ],
)
def test_save_settings(
    mocked_client,
    api_endpoint,
    old_api_endpoint,
    dataset_name,
    clear_all_datasets,
    task,
    settings,
):
    response = mocked_client.post(
        f"{api_endpoint}/{task}",
        json={"name": dataset_name},
    )
    assert response.status_code == 200

    response = mocked_client.put(
        f"{api_endpoint}/{task}/{dataset_name}/settings",
        json=settings.dict(),
    )

    assert response.status_code == 200, response.json()
    created_settings = settings.__class__.parse_obj(response.json())
    assert created_settings == settings
