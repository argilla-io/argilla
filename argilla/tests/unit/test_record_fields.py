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

from argilla import Record, Suggestion
from argilla.records._resource import RecordSuggestions


class TestRecordFields:
    def test_create_record_fields(self):
        record = Record(fields={"name": "John Doe"}, metadata={"age": 30})

        fields = record.fields
        assert fields["name"] == "John Doe"
        assert record.metadata["age"] == 30

    def test_create_record_image_path(self):
        record = Record(fields={"image": "path/to/image.jpg"})

        fields = record.fields
        assert fields["image"] == "path/to/image.jpg"
