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
import uuid

import pytest

from argilla import Argilla, Dataset, Settings, TextField, RatingQuestion


@pytest.fixture(scope="session", autouse=True)
def clean_datasets(client: Argilla):
    datasets = client.datasets
    for dataset in datasets:
        if dataset.name.startswith("test_"):
            dataset.delete()
    yield


class TestCreateDatasets:
    def test_create_dataset(self, client: Argilla):
        dataset_name = f"test_dataset_{uuid.uuid4()}"
        dataset = Dataset(
            name=dataset_name,
            settings=Settings(
                fields=[TextField(name="test_field")],
                questions=[RatingQuestion(name="test_question", values=[1, 2, 3, 4, 5])],
            ),
        )
        client.datasets.add(dataset)

        assert dataset in client.datasets
        assert dataset.exists()

        created_dataset = client.datasets(name=dataset_name)
        assert created_dataset.settings == dataset.settings

    def test_create_multiple_dataset_with_same_settings(self, client: Argilla):
        dataset_name = f"test_dataset_{uuid.uuid4()}"

        settings = Settings(
            fields=[TextField(name="text")],
            questions=[RatingQuestion(name="question", values=[1, 2, 3, 4, 5])],
        )
        dataset = Dataset(name=dataset_name, settings=settings, client=client).create()
        dataset2 = Dataset(name=f"{dataset_name}_2", settings=settings, client=client).create()

        assert dataset in client.datasets
        assert dataset2 in client.datasets

        assert dataset.exists()
        assert dataset2.exists()

        for ds in [dataset, dataset2]:
            schema = client.datasets(name=ds.name).schema

            assert isinstance(schema["text"], TextField)
            assert schema["text"].name == "text"
            assert isinstance(schema["question"], RatingQuestion)
            assert schema["question"].name == "question"
            assert schema["question"].values == [1, 2, 3, 4, 5]

    def test_create_dataset_from_existing_dataset(self, client: Argilla):
        dataset_name = f"test_dataset_{uuid.uuid4()}"
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
