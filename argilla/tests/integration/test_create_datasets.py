# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from argilla import Argilla, Dataset, Settings, TextField, RatingQuestion, LabelQuestion, Workspace
from argilla.settings._task_distribution import TaskDistribution


@pytest.fixture(scope="session", autouse=True)
def clean_datasets(client: Argilla):
    datasets = client.datasets
    for dataset in datasets:
        if dataset.name.startswith("test_"):
            dataset.delete()
    yield


class TestCreateDatasets:
    def test_create_dataset(self, client: Argilla, dataset_name: str):
        dataset = Dataset(
            name=dataset_name,
            settings=Settings(
                fields=[TextField(name="test_field")],
                questions=[RatingQuestion(name="test_question", values=[1, 2, 3, 4, 5])],
            ),
        )
        client.datasets.add(dataset)

        assert dataset in client.datasets
        assert dataset is not None

        created_dataset = client.datasets(name=dataset_name)
        assert created_dataset.settings == dataset.settings
        assert created_dataset.settings.distribution == TaskDistribution(min_submitted=1)

    def test_create_multiple_dataset_with_same_settings(self, client: Argilla, dataset_name: str):
        settings = Settings(
            fields=[TextField(name="text")],
            questions=[RatingQuestion(name="question", values=[1, 2, 3, 4, 5])],
        )
        dataset = Dataset(name=dataset_name, settings=settings, client=client).create()
        dataset2 = Dataset(name=f"{dataset_name}_2", settings=settings, client=client).create()

        assert dataset in client.datasets
        assert dataset2 in client.datasets

        assert client.api.datasets.exists(dataset.id)
        assert client.api.datasets.exists(dataset2.id)

        for ds in [dataset, dataset2]:
            schema = client.datasets(name=ds.name).schema

            assert isinstance(schema["text"], TextField)
            assert schema["text"].name == "text"
            assert isinstance(schema["question"], RatingQuestion)
            assert schema["question"].name == "question"
            assert schema["question"].values == [1, 2, 3, 4, 5]

    def test_create_dataset_from_existing_dataset(self, client: Argilla, dataset_name: str):
        dataset = Dataset(
            name=dataset_name,
            settings=Settings(
                fields=[TextField(name="text")],
                questions=[RatingQuestion(name="question", values=[1, 2, 3, 4, 5])],
            ),
        ).create()

        assert dataset in client.datasets
        created_dataset = client.datasets(dataset.name)

        dataset_copy = Dataset(name=f"{dataset.name}_copy", settings=created_dataset.settings, client=client).create()
        assert dataset_copy in client.datasets

        schema = dataset_copy.schema
        assert isinstance(schema["text"], TextField)
        assert schema["text"].name == "text"
        assert isinstance(schema["question"], RatingQuestion)
        assert schema["question"].name == "question"
        assert schema["question"].values == [1, 2, 3, 4, 5]

    def test_copy_datasets_from_different_clients(self, client: Argilla, dataset_name: str):
        dataset = Dataset(
            name=dataset_name,
            settings=Settings(
                fields=[TextField(name="text")],
                questions=[RatingQuestion(name="question", values=[1, 2, 3, 4, 5])],
            ),
            client=client,
        ).create()

        new_client = Argilla()
        new_ws = Workspace("test_copy_workspace")
        new_client.workspaces.add(new_ws)

        new_dataset = Dataset(
            name=dataset.name,
            workspace=new_ws,
            settings=dataset.settings,
            client=new_client,
        ).create()

        assert new_dataset._client == new_client
        assert dataset._client != new_dataset._client

        assert dataset.settings != new_dataset.settings

        assert isinstance(new_dataset.settings.fields["text"], TextField)
        assert len(new_dataset.settings.questions) == 1
        for question in new_dataset.settings.questions:
            assert question.name == "question"

    def test_create_a_dataset_copy(self, client: Argilla, dataset_name: str):
        dataset = Dataset(
            name=dataset_name,
            settings=Settings(
                fields=[TextField(name="text")],
                questions=[RatingQuestion(name="question", values=[1, 2, 3, 4, 5])],
            ),
        ).create()

        dataset.records.log([{"text": "This is a text"}])

        new_dataset = Dataset(
            name=f"{dataset_name}_copy",
            settings=dataset.settings,
        ).create()

        records = list(dataset.records)
        new_dataset.records.log(records)

        assert len(list(dataset.records)) == len(list(new_dataset.records))
        assert dataset.distribution == new_dataset.distribution

    def test_create_dataset_with_custom_task_distribution(self, client: Argilla, dataset_name: str):
        task_distribution = TaskDistribution(min_submitted=4)

        settings = Settings(
            fields=[TextField(name="text", title="text")],
            questions=[LabelQuestion(name="label", title="text", labels=["positive", "negative"])],
            distribution=task_distribution,
        )
        dataset = Dataset(dataset_name, settings=settings).create()

        assert client.api.datasets.exists(dataset.id)
        assert dataset.settings.distribution == task_distribution
