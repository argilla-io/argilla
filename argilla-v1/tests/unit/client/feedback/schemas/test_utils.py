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

from argilla_v1.client.feedback.schemas.utils import LabelMappingMixin

from tests.pydantic_v1 import BaseModel, Field


def test_label_mapping_mixin() -> None:
    class TestLabelMappingMixin(BaseModel, LabelMappingMixin):
        server_settings: dict = Field(default_factory=dict)

    my_class = TestLabelMappingMixin(server_settings={"options": [{"value": "label1"}, {"value": "label2"}]})
    assert my_class.__all_labels__ == ["label1", "label2"]
    assert my_class.__label2id__ == {"label1": 0, "label2": 1}
    assert my_class.__id2label__ == {0: "label1", 1: "label2"}
