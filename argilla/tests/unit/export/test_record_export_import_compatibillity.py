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

import json
import uuid

import pytest

import argilla as rg
from argilla.records._resource import Record


@pytest.fixture
def record():
    return rg.Record(
        id=uuid.uuid4(),
        fields={"text": "Hello World, how are you?"},
        suggestions=[
            rg.Suggestion("label", "positive", score=0.9),
            rg.Suggestion("topics", ["topic1", "topic2"], score=[0.9, 0.8]),
        ],
        responses=[rg.Response("label", "positive", user_id=uuid.uuid4())],
        metadata={"source": "twitter", "language": "en"},
        vectors={"text": [0, 0, 0]},
    )


def test_export_record_to_from_dict(record):
    record_dict = record.to_dict()
    imported_record = rg.Record.from_dict(record_dict)

    assert record.responses["label"][0].value == imported_record.responses["label"][0].value
    assert record.suggestions["topics"].value == imported_record.suggestions["topics"].value
    for key, value in record.metadata.items():
        assert imported_record.metadata[key] == value
    assert record.fields["text"] == imported_record.fields["text"]
    # This is a consequence of how UUIDs are treated in python and could be
    #  problematic for users.
    assert str(record.id) == imported_record.id


def test_export_generic_io_via_json(record):
    record_dict = record.to_dict()
    record_dict = json.dumps(record_dict)
    record_dict = json.loads(record_dict)
    imported_record = Record.from_dict(record_dict)

    assert record.responses["label"][0].value == imported_record.responses["label"][0].value
    assert record.suggestions["topics"].value == imported_record.suggestions["topics"].value
    for key, value in record.metadata.items():
        assert imported_record.metadata[key] == value
    assert record.fields["text"] == imported_record.fields["text"]
    assert record.vectors["text"] == imported_record.vectors["text"]
