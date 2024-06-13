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

from argilla_v1.client.apis.datasets import TextClassificationSettings


def test_text_classification_settings_preserve_labels_order() -> None:
    settings = TextClassificationSettings(
        label_schema=[
            "1 (extremely positive/supportive)",
            "2 (positive/supportive)",
            "3 (neutral)",
            "4 (hateful/unsupportive)",
            "5 (extremely hateful/unsupportive)",
            "6 (can't say!)",
            "6 (can't say!)",
            "6 (can't say!)",
        ]
    )

    assert settings.label_schema == [
        "1 (extremely positive/supportive)",
        "2 (positive/supportive)",
        "3 (neutral)",
        "4 (hateful/unsupportive)",
        "5 (extremely hateful/unsupportive)",
        "6 (can't say!)",
    ]
