#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from typing import List, Union

import argilla_v1.client.singleton as rg
import pytest
from argilla_v1 import User, Workspace
from argilla_v1.feedback import (
    FeedbackDataset,
    FeedbackRecord,
    ResponseSchema,
    TextField,
    TextQuestion,
    VectorSettings,
)


@pytest.fixture
def feedback_dataset() -> FeedbackDataset:
    return FeedbackDataset(fields=[TextField(name="text")], questions=[TextQuestion(name="question")])


class TestSuiteWorkingWithVectors:
    def tests_find_similar_records_using_value(self, owner: User, feedback_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test")

        feedback_dataset.add_vector_settings(VectorSettings(name="vector", dimensions=2))

        feedback_dataset.add_records(
            [
                FeedbackRecord(external_id="0", fields={"text": "hello"}, vectors={"vector": [1, 2]}),
                FeedbackRecord(external_id="1", fields={"text": "hello"}, vectors={"vector": [3, 4]}),
                FeedbackRecord(external_id="2", fields={"text": "hello"}, vectors={"vector": [5, 6]}),
            ]
        )

        remote = feedback_dataset.push_to_argilla("test_find_similar_records", workspace=workspace)

        records_with_scores = remote.find_similar_records(vector_name="vector", value=[1, 2], max_results=2)
        assert len(records_with_scores) == 2

        record, score = records_with_scores[0]
        assert record.external_id == "0"
        assert score == 1.0

        record, score = records_with_scores[1]
        assert record.external_id == "1"
        assert score < 1.0

    def test_find_similar_records_using_record(self, owner: User, feedback_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test")

        feedback_dataset.add_vector_settings(VectorSettings(name="vector", dimensions=2))

        feedback_dataset.add_records(
            [
                FeedbackRecord(external_id="0", fields={"text": "hello"}, vectors={"vector": [1, 2]}),
                FeedbackRecord(external_id="1", fields={"text": "hello"}, vectors={"vector": [3, 4]}),
                FeedbackRecord(external_id="2", fields={"text": "hello"}, vectors={"vector": [5, 6]}),
            ]
        )

        remote = feedback_dataset.push_to_argilla("test_find_similar_records", workspace=workspace)

        reference_record = remote[0]

        records_with_scores = remote.find_similar_records(vector_name="vector", record=reference_record, max_results=2)
        assert len(records_with_scores) == 2

        record, score = records_with_scores[0]
        assert record.external_id == "1"
        assert score < 1.0

        record, score = records_with_scores[1]
        assert record.external_id == "2"
        assert score < 1.0

    @pytest.mark.skip(
        reason="Review this test since this is the ONLY order where all tests pass. "
        "If you change the order, some of those tests will fail with unexpected vector names."
    )
    @pytest.mark.parametrize(
        "vector_names",
        [
            ["vector1", "vector2", "vector3"],
            ["vector1", "vector2"],
            ["vector2", "vector3"],
            ["vector1", "vector3"],
            ["vector1"],
            ["vector3"],
            ["vector2"],
            "vector1",
        ],
    )
    def test_load_dataset_including_selective_vectors(self, owner: User, vector_names: Union[str, List[str]]):
        rg.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test")

        feedback_dataset = FeedbackDataset(
            fields=[TextField(name="text")],
            questions=[TextQuestion(name="question")],
            vectors_settings=[
                VectorSettings(name="vector1", dimensions=2),
                VectorSettings(name="vector2", dimensions=2),
                VectorSettings(name="vector3", dimensions=2),
            ],
        )

        feedback_dataset.add_records(
            [
                FeedbackRecord(
                    external_id="0",
                    fields={"text": "hello"},
                    vectors={vector_settings.name: [1, 2] for vector_settings in feedback_dataset.vectors_settings},
                ),
                FeedbackRecord(
                    external_id="1",
                    fields={"text": "hello"},
                    vectors={vector_settings.name: [3, 4] for vector_settings in feedback_dataset.vectors_settings},
                ),
                FeedbackRecord(
                    external_id="2",
                    fields={"text": "hello"},
                    vectors={vector_settings.name: [5, 6] for vector_settings in feedback_dataset.vectors_settings},
                ),
            ]
        )

        remote = feedback_dataset.push_to_argilla("test_find_similar_records", workspace=workspace)
        remote = FeedbackDataset.from_argilla(id=remote.id, with_vectors=vector_names)

        if not isinstance(vector_names, list):
            vector_names = [vector_names]

        expected_vector_names = set(vector_names)

        assert set(remote[0].vectors.keys()) == expected_vector_names
        assert set(remote[1].vectors.keys()) == expected_vector_names
        assert set(remote[2].vectors.keys()) == expected_vector_names

    def test_load_dataset_including_wrong_vectors(self, owner: User, feedback_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test")

        feedback_dataset.add_vector_settings(VectorSettings(name="vector", dimensions=2))
        feedback_dataset.add_records(
            [
                FeedbackRecord(external_id="0", fields={"text": "hello"}, vectors={"vector": [1, 2]}),
                FeedbackRecord(external_id="1", fields={"text": "hello"}, vectors={"vector": [3, 4]}),
                FeedbackRecord(external_id="2", fields={"text": "hello"}, vectors={"vector": [5, 6]}),
            ]
        )

        remote = feedback_dataset.push_to_argilla("test_find_similar_records", workspace=workspace)
        with pytest.raises(
            ValueError,
            match="The vector name `wrong-vector-name` does not exist in the current `FeedbackDataset` in Argilla. "
            "The existing vector names are: \['vector'\].",
        ):
            FeedbackDataset.from_argilla(id=remote.id, with_vectors="wrong-vector-name")

    def test_find_similar_including_vectors(self, owner: User, feedback_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test")

        feedback_dataset.add_vector_settings(VectorSettings(name="vector", dimensions=2))
        feedback_dataset.add_vector_settings(VectorSettings(name="vector_b", dimensions=2))
        feedback_dataset.add_records(
            [
                FeedbackRecord(
                    external_id="0", fields={"text": "hello"}, vectors={"vector": [1, 2], "vector_b": [1, 2]}
                ),
                FeedbackRecord(
                    external_id="1", fields={"text": "hello"}, vectors={"vector": [3, 4], "vector_b": [3, 4]}
                ),
                FeedbackRecord(external_id="2", fields={"text": "hello"}, vectors={"vector": [5, 6]}),
            ]
        )

        remote = feedback_dataset.push_to_argilla("test_find_similar_records", workspace=workspace)
        remote = FeedbackDataset.from_argilla(id=remote.id, with_vectors="all")

        records_with_score = remote.find_similar_records(vector_name="vector", value=[1, 2], max_results=3)

        records = [record for record, _ in records_with_score]
        assert records[0].vectors.keys() == {"vector", "vector_b"}
        assert records[1].vectors.keys() == {"vector", "vector_b"}
        assert records[2].vectors.keys() == {"vector"}

    def test_find_similar_combining_filters(self, owner: User, feedback_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test")

        feedback_dataset.add_vector_settings(VectorSettings(name="vector", dimensions=2))

        feedback_dataset.add_records(
            [
                FeedbackRecord(external_id="0", fields={"text": "hello"}, vectors={"vector": [1, 2]}),
                FeedbackRecord(
                    external_id="1",
                    fields={"text": "hello"},
                    vectors={"vector": [3, 4]},
                    responses=[ResponseSchema(status="discarded")],
                ),
                FeedbackRecord(
                    external_id="2",
                    fields={"text": "hello"},
                    vectors={"vector": [5, 6]},
                    responses=[ResponseSchema(status="submitted", values={"question": {"value": "answer"}})],
                ),
            ]
        )

        remote = feedback_dataset.push_to_argilla("test_find_similar_records", workspace=workspace)
        only_submitted_and_discarded_records = remote.filter_by(response_status=["submitted", "discarded"])

        records_with_scores = only_submitted_and_discarded_records.find_similar_records(
            vector_name="vector",
            value=[1, 2],
            max_results=3,
        )

        assert len(records_with_scores) == 2

        record, score = records_with_scores[0]
        assert record.external_id == "1"
        assert score < 1.0

        record, score = records_with_scores[1]
        assert record.external_id == "2"
        assert score < 1.0

    def test_find_similar_with_wrong_inputs(self, owner: User, feedback_dataset: FeedbackDataset):
        rg.init(api_key=owner.api_key)
        workspace = Workspace.create(name="test")

        record = FeedbackRecord(external_id="0", fields={"text": "hello"}, vectors={"vector": [1, 2]})

        feedback_dataset.add_vector_settings(VectorSettings(name="vector", dimensions=2))
        remote = feedback_dataset.push_to_argilla("test_find_similar_records", workspace=workspace)

        with pytest.raises(ValueError, match="Either 'record' or 'value' must be provided"):
            remote.find_similar_records(vector_name="vector")

        with pytest.raises(ValueError, match="Either 'record' or 'value' must be provided"):
            remote.find_similar_records(vector_name="vector", value=[1, 2], record=record)
