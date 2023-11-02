import pytest
import argilla as rg

from argilla import User, Workspace
from argilla.feedback import (
    FeedbackDataset,
    FeedbackRecord,
    TextField,
    TextQuestion,
    VectorSettings,
    ResponseSchema,
)


@pytest.fixture
def feedback_dataset() -> FeedbackDataset:
    return FeedbackDataset(fields=[TextField(name="text")], questions=[TextQuestion(name="question")])


class TestSuiteFindSimilar:
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
