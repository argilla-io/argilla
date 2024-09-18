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

from argilla.records import Filter


class TestFilters:
    def test_filter_by_responses_status(self):
        test_filter = Filter(("response.status", "in", ["submitted", "discard"]))
        assert test_filter.api_model().model_dump(by_alias=True) == {
            "type": "and",
            "and": [
                {
                    "scope": {"entity": "response", "property": "status", "question": None},
                    "type": "terms",
                    "values": ["submitted", "discard"],
                }
            ],
        }
