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

from argilla_server.models import Field
from argilla_server.enums import FieldType


@pytest.mark.asyncio
class TestFieldModel:
    def test_is_text_property(self):
        assert Field(settings={"type": FieldType.text}).is_text == True
        assert Field(settings={"type": FieldType.image}).is_text == False
        assert Field(settings={"type": FieldType.chat}).is_text == False
        assert Field(settings={}).is_text == False

    def test_is_image_property(self):
        assert Field(settings={"type": FieldType.image}).is_image == True
        assert Field(settings={"type": FieldType.text}).is_image == False
        assert Field(settings={"type": FieldType.chat}).is_image == False
        assert Field(settings={}).is_image == False

    def test_is_chat_property(self):
        assert Field(settings={"type": FieldType.chat}).is_chat == True
        assert Field(settings={"type": FieldType.text}).is_chat == False
        assert Field(settings={"type": FieldType.image}).is_chat == False
        assert Field(settings={}).is_chat == False
