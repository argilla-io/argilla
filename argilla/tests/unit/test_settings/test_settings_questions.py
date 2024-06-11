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


class TestQuestions:
    def test_label_question_init(self):
        labels = ["label1", "label2", "label3"]
        question = rg.LabelQuestion(name="label_question", labels=labels)
        assert question.name == "label_question"
        assert question.labels == ["label1", "label2", "label3"]

    def test_label_question_init_with_dict(self):
        labels = {"label1": "1", "label2": "2", "label3": "3"}
        question = rg.LabelQuestion(name="label_question", labels=labels)
        assert question.name == "label_question"
        assert question.labels == ["label1", "label2", "label3"]
        text_of_labels = [label["text"] for label in question._model.settings.options]
        for i in range(len(labels)):
            assert text_of_labels[i] == list(labels.values())[i]

    def test_rating_question_init(self):
        question = rg.RatingQuestion(name="rating_question", values=[1, 2, 3])
        assert question.name == "rating_question"
        assert question.values == [1, 2, 3]

    def test_text_question_init(self):
        question = rg.TextQuestion(name="text_question", use_markdown=True)
        assert question.name == "text_question"
        assert question.use_markdown is True

    def test_multi_label_question_init(self):
        labels = ["label1", "label2", "label3"]
        question = rg.MultiLabelQuestion(name="multi_label_question", labels=labels, visible_labels=3)
        assert question.name == "multi_label_question"
        assert question.labels == ["label1", "label2", "label3"]
        assert question.visible_labels == 3

    def test_multi_label_question_init_with_dict(self):
        labels = {"label1": "1", "label2": "2", "label3": "3"}
        question = rg.MultiLabelQuestion(name="multi_label_question", labels=labels, visible_labels=3)
        assert question.name == "multi_label_question"
        assert question.labels == ["label1", "label2", "label3"]
        assert question.visible_labels == 3

    def test_multi_label_question_init_ordered(self):
        question = rg.MultiLabelQuestion(
            name="multi_label_question",
            labels=["label1", "label2", "label3"],
            visible_labels=3,
            labels_order="suggestion",
        )
        assert question.name == "multi_label_question"
        assert question.labels == ["label1", "label2", "label3"]
        assert question.visible_labels == 3

    def test_ranking_question_init(self):
        question = rg.RankingQuestion(name="ranking_question", values=["rank-a", "rank-b"])
        assert question.name == "ranking_question"
        assert question.values == ["rank-a", "rank-b"]
