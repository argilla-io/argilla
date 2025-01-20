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

from argilla import Argilla, Dataset, Settings, TextField, TextQuestion, Workspace, TaskDistribution


class TestDatasetsList:
    def test_list_datasets(self, client: Argilla):
        workspace = Workspace(name="test_workspace", client=client)
        workspace.create()

        dataset = Dataset(
            name="test_dataset",
            workspace=workspace.name,
            settings=Settings(fields=[TextField(name="text")], questions=[TextQuestion(name="text_question")]),
            client=client,
        )
        dataset.create()
        datasets = client.datasets
        assert len(datasets) > 0, "No datasets were found"

        for ds in datasets:
            if ds.name == "test_dataset":
                assert ds == dataset, "The dataset was not loaded properly"

    def test_list_dataset_with_custom_task_distribution(self, client: Argilla, workspace: Workspace):
        dataset = Dataset(
            name="test_dataset",
            workspace=workspace.name,
            settings=Settings(
                fields=[TextField(name="text")],
                questions=[TextQuestion(name="text_question")],
                distribution=TaskDistribution(min_submitted=4),
            ),
            client=client,
        )
        dataset.create()
        datasets = client.datasets
        assert len(datasets) > 0, "No datasets were found"

        dataset_idx = 0
        for idx, ds in enumerate(datasets):
            if ds.id == dataset.id:
                dataset_idx = idx
                assert ds.settings.distribution.min_submitted == 4, "The dataset was not loaded properly"
                break

        ds = client.datasets[dataset_idx]
        assert ds.settings.distribution.min_submitted == 4, "The dataset was not loaded properly"
