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

from argilla.server.daos.backend.mappings.helpers import mappings


def text_classification_mappings():
    """Text classification index mappings"""
    return {
        "_source": mappings.source(
            excludes=[
                "predicted",
                "predicted_as",
                "predicted_by",
                "annotated_as",
                "annotated_by",
                "score",
            ]
        ),
        "properties": {
            "inputs": {
                "type": "object",
                "dynamic": True,
            },
            "explanation": {
                "type": "object",
                "dynamic": True,
                "enabled": False,  # Won't search by explanation
            },
            "predicted": mappings.keyword_field(),
            "multi_label": {"type": "boolean"},
            "annotated_as": mappings.keyword_field(enable_text_search=True),
            "predicted_as": mappings.keyword_field(enable_text_search=True),
            "score": mappings.decimal_field(),
        },
        "dynamic_templates": [
            {
                "inputs.*": {
                    "path_match": "inputs.*",
                    "mapping": mappings.text_field(),
                }
            }
        ],
    }
