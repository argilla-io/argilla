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
import argilla as rg


class TestTextField:
    def test_init_text_field(self):
        mock_name = "prompt"
        mock_use_markdown = True
        text_field = rg.TextField(name=mock_name, use_markdown=mock_use_markdown)
        assert text_field.name == mock_name
        assert text_field.use_markdown == mock_use_markdown
        assert text_field.title == mock_name
        assert text_field.required is True

    def test_init_text_field_with_title(self):
        mock_name = "prompt"
        mock_use_markdown = True
        mock_title = "Prompt"
        text_field = rg.TextField(name=mock_name, use_markdown=mock_use_markdown, title=mock_title)
        assert text_field.name == mock_name
        assert text_field.use_markdown == mock_use_markdown
        assert text_field.title == mock_title
        assert text_field.required is True

    @pytest.mark.parametrize(
        "name, expected",
        [
            ("prompt", "prompt"),
            ("Prompt", "prompt"),
            ("Prompt Name", "prompt_name"),
            ("Prompt Name 2", "prompt_name_2"),
            ("Prompt Name 2", "prompt_name_2"),
        ],
    )
    def test_name_validator(self, name, expected, mocker):
        mock_use_markdown = True
        text_field = rg.TextField(name=name, use_markdown=mock_use_markdown)
        assert text_field.name == expected

    @pytest.mark.parametrize(
        "title, name, expected",
        [
            (None, "prompt", "prompt"),
            ("Prompt", "prompt", "Prompt"),
            ("Prompt", "prompt", "Prompt"),
        ],
    )
    def test_title_validator(self, title, name, expected, mocker):
        mock_use_markdown = True
        text_field = rg.TextField(name=name, use_markdown=mock_use_markdown, title=title)
        assert text_field.title == expected


class TestChatField:
    def test_create_chat_field(self):
        field = rg.ChatField(name="chat")

        assert field.name == "chat"
        assert field.use_markdown is True

    def test_create_chat_field_with_use_markdown(self):
        field = rg.ChatField(name="chat", use_markdown=False)

        assert field.name == "chat"
        assert field.use_markdown is False

    def test_update_chat_field_use_markdown(self):
        field = rg.ChatField(name="chat", use_markdown=True)
        field.use_markdown = False

        assert field.use_markdown is False


class TestCustomField:
    def test_create_custom_field(self):
        field = rg.CustomField(name="custom", template="<p>{{ custom }}</p>")

        assert field.name == "custom"
        assert field.template == "<p>{{ custom }}</p>"
        assert field.advanced_mode is False

    def test_create_custom_field_with_advanced_mode(self):
        field = rg.CustomField(name="custom", template="<p></p>", advanced_mode=True)

        assert field.name == "custom"
        assert field.template == "<p></p>"
        assert field.advanced_mode is True
