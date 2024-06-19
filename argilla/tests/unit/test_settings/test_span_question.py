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

import argilla as rg


class TestSpanQuestions:
    def test_create_question(self):
        question = rg.SpanQuestion(
            name="span_question", field="field", allow_overlapping=True, labels=["label1", "label2", "label3"]
        )
        assert question.name == "span_question"
        assert question.field == "field"
        assert question.allow_overlapping is True
        assert question.labels == ["label1", "label2", "label3"]
        assert question.visible_labels == 3

    def test_change_field_value(self):
        question = rg.SpanQuestion(
            name="span_question", field="field", allow_overlapping=True, labels=["label1", "label2"]
        )
        question.field = "new_field"
        assert question.field == "new_field"

    def test_change_allow_overlapping_value(self):
        question = rg.SpanQuestion(
            name="span_question", field="field", allow_overlapping=True, labels=["label1", "label2"]
        )
        question.allow_overlapping = False
        assert question.allow_overlapping is False

    def test_change_labels_value(self):
        question = rg.SpanQuestion(
            name="span_question", field="field", allow_overlapping=True, labels=["label1", "label2", "label3"]
        )
        question.labels = ["label1", "label2"]
        assert question.labels == ["label1", "label2"]
        assert question.visible_labels == 3
