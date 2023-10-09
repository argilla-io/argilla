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

import pytest
from argilla.client.feedback.dataset.local import FeedbackDataset
from argilla.client.feedback.schemas.fields import TextField
from argilla.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla.client.feedback.schemas.questions import TextQuestion
from argilla.client.feedback.schemas.records import FeedbackRecord


@pytest.mark.parametrize(
    "record",
    [
        FeedbackRecord(fields={"required-field": "text"}, metadata={"nested-metadata": {"a": 1}}),
        FeedbackRecord(
            fields={"required-field": "text", "optional-field": "text"},
            metadata={"int-metadata": 1, "float-metadata": 1.0},
        ),
        FeedbackRecord(
            fields={"required-field": "text", "optional-field": None},
            metadata={"terms-metadata": "a", "more-metadata": 3},
        ),
    ],
)
def test_add_records_validation(record: "FeedbackRecord") -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )

    dataset.add_records(record)
    assert len(dataset.records) == 1
    assert dataset.records[0] == record


@pytest.mark.parametrize(
    "record, exception_cls, exception_msg",
    [
        (FeedbackRecord(fields={}, metadata={}), ValueError, "required-field\n  field required"),
        (
            FeedbackRecord(fields={"optional-field": "text"}, metadata={}),
            ValueError,
            "required-field\n  field required",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"terms-metadata": "d"}),
            ValueError,
            "terms-metadata\n  Provided 'terms-metadata=d' is not valid, only values in \['a', 'b', 'c'\] are allowed.",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"int-metadata": 11}),
            ValueError,
            "int-metadata\n  Provided 'int-metadata=11' is not valid, only values between 0 and 10 are allowed.",
        ),
        (
            FeedbackRecord(fields={"required-field": "text"}, metadata={"float-metadata": 11.0}),
            ValueError,
            "float-metadata\n  Provided 'float-metadata=11.0' is not valid, only values between 0.0 and 10.0 are allowed.",
        ),
    ],
)
def test_add_records_validation_error(record: FeedbackRecord, exception_cls: Exception, exception_msg: str) -> None:
    dataset = FeedbackDataset(
        fields=[TextField(name="required-field", required=True), TextField(name="optional-field", required=False)],
        questions=[TextQuestion(name="question", required=True)],
        metadata_properties=[
            TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
            IntegerMetadataProperty(name="int-metadata", min=0, max=10),
            FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
        ],
    )

    with pytest.raises(exception_cls, match=exception_msg):
        dataset.add_records(record)
    assert len(dataset.records) == 0
