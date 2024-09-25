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

from typing import Dict, List

import markdown

CHAT_CSS_STYLE = """
    <style>
        .user-message, .system-message {
            display: flex;
            margin: 10px;
        }
        .user-message {
            justify-content: flex-end;
        }
        .system-message {
            justify-content: flex-start;
        }
        .user-message .message-content {
            background-color: #c2e3f7;
            color: #000000;
        }
        .system-message .message-content {
            background-color: #f5f5f5;
            color: #000000;
        }
        .message-content {
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
        }
    </style>
    """


def chat_to_html(messages: List[Dict[str, str]]) -> str:
    """
    Converts a list of chat messages in the OpenAI format to HTML.

    Args:
        messages (List[Dict[str, str]]): A list of dictionaries where each dictionary represents a chat message.
            Each dictionary should have the keys:
                - "role": A string indicating the role of the sender (e.g., "user", "model", "assistant", "system").
                - "content": The content of the message.

    Returns:
        str: An HTML string that represents the chat conversation.

    Raises:
        ValueError: If the an invalid role is passed.

    Examples:
        ```python
        from argilla.markdown import chat_to_html
        html = chat_to_html([
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "goodbye"}
        ])
        ```
    """
    chat_html = ""
    for message in messages:
        role = message["role"]
        content = message["content"]
        content_html = markdown.markdown(content)

        if role == "user":
            html = '<div class="user-message">' + '<div class="message-content">'
        elif role in ["model", "assistant", "system"]:
            html = '<div class="system-message">' + '<div class="message-content">'
        else:
            raise ValueError(f"Invalid role: {role}")

        html += f"{content_html}"
        html += "</div></div>"
        chat_html += html

    return f"<body>{CHAT_CSS_STYLE}{chat_html}</body>"
