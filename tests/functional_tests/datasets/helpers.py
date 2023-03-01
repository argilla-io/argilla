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

import argilla as rg
from argilla import Text2TextRecord, TextClassificationRecord, TokenClassificationRecord
from argilla.server.commons.models import TaskType


def create_dataset(task: TaskType):
    def text_class(idx):
        return TextClassificationRecord(
            id=idx,
            text="This is the text",
        )

    def token_class(idx):
        return TokenClassificationRecord(
            id=idx,
            text="This is the text",
            tokens="This is the text".split(),
        )

    def text2text(idx):
        return Text2TextRecord(
            id=idx,
            text="This is the text",
        )

    dataset = "test_dataset"
    rg.delete(dataset)

    if task == TaskType.text_classification:
        record_builder = text_class
    elif task == TaskType.token_classification:
        record_builder = token_class
    else:
        record_builder = text2text

    records = [record_builder(i) for i in range(0, 50)]

    rg.log(
        name=dataset,
        records=records,
    )

    return dataset
