#  coding=utf-8
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
import rubrix as rb
from rubrix.metrics.commons import records_status, text_length


def test_status_distribution(mocked_client):
    dataset = "test_status_distribution"

    rb.delete(dataset)

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                inputs={"text": "my first rubrix example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my second rubrix example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
                status="Default",
            ),
        ],
        name=dataset,
    )

    results = records_status(dataset)
    assert results
    assert results.data == {"Default": 1, "Validated": 1}
    results.visualize()


def test_text_length(mocked_client):
    dataset = "test_text_length"

    rb.delete(dataset)

    rb.log(
        [
            rb.TextClassificationRecord(
                id=1,
                inputs={"text": "my first rubrix example"},
                prediction=[("spam", 0.8), ("ham", 0.2)],
                annotation=["spam"],
            ),
            rb.TextClassificationRecord(
                id=2,
                inputs={"text": "my second rubrix example"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
                status="Default",
            ),
            rb.TextClassificationRecord(
                id=3,
                inputs={"text": "simple text"},
                prediction=[("ham", 0.8), ("spam", 0.2)],
                annotation=["ham"],
            ),
        ],
        name=dataset,
    )

    results = text_length(dataset)
    assert results
    assert results.data == {
        "11.0": 1,
        "12.0": 0,
        "13.0": 0,
        "14.0": 0,
        "15.0": 0,
        "16.0": 0,
        "17.0": 0,
        "18.0": 0,
        "19.0": 0,
        "20.0": 0,
        "21.0": 0,
        "22.0": 0,
        "23.0": 1,
        "24.0": 1,
    }
    results.visualize()
