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

from typing import Iterable, Tuple

from argilla.client import api
from argilla.client.apis.labeling import Rule, TokenClassificationLabelingRules


def test_get_rule_without_results(
    mocked_client,
    log_tokenclassification_records,
):

    dataset = log_tokenclassification_records
    client = api.active_api().client
    query = "no-data"

    ds = api.load(
        name=dataset,
        query=query,
    )
    assert len(ds) == 0

    labeling = TokenClassificationLabelingRules(client)
    annotations = labeling.rule_annotations(
        dataset=dataset,
        rule=Rule(
            query=query,
            label="BLAS",
        ),
    )
    assert list(annotations) == []


def test_get_rule_annotations(
    mocked_client,
    log_tokenclassification_records,
):
    dataset = log_tokenclassification_records
    client = api.active_api().client
    query = "example"
    label = "BLAS"

    ds = api.load(
        name=dataset,
        query=query,
    )
    assert len(ds) > 0

    labeling = TokenClassificationLabelingRules(client)

    annotations = labeling.rule_annotations(
        dataset=dataset,
        rule=Rule(
            query=query,
            label=label,
        ),
    )

    annotations = list(annotations)
    assert annotations == [
        ("1", [(label, 11, 18)]),
        ("2", [(label, 17, 24)]),
        ("3", [(label, 18, 25)]),
        ("a", [(label, 16, 23)]),
        ("b", [(label, 16, 23)]),
    ]


def test_get_rule_annotations_with_pagination_steps(
    mocked_client,
    log_a_lot_of_token_classification_records,
):
    dataset = log_a_lot_of_token_classification_records
    client = api.active_api().client
    query = "example"
    label = "BLAS"

    ds = api.load(
        name=dataset,
        query=query,
    )
    assert len(ds) > 0
    labeling = TokenClassificationLabelingRules(client)

    for chunk_size in range(1, len(ds)):
        annotations = labeling.rule_annotations(
            dataset=dataset,
            rule=Rule(
                query=query,
                label=label,
            ),
            chunk_size=chunk_size,
        )

        annotations = list(annotations)
        assert len(ds) == len(annotations)


def test_get_rule_annotations_by_record_ids(
    mocked_client,
    log_tokenclassification_records,
):
    dataset = log_tokenclassification_records
    client = api.active_api().client
    query = "example"
    label = "BLAS"

    ds = api.load(
        name=dataset,
        query=query,
    )
    assert len(ds) > 0

    labeling = TokenClassificationLabelingRules(client)
    ids = [ds[0].id, ds[1].id]

    annotations = to_annotations_map(
        labeling.rule_annotations(
            dataset=dataset,
            ids=ids,
            rule=Rule(
                query=query,
                label=label,
            ),
        )
    )
    assert len(annotations) == len(ids)

    baseline_annotations = to_annotations_map(
        labeling.rule_annotations(
            dataset=dataset,
            ids=ids,
            rule=Rule(
                query=query,
                label=label,
            ),
        )
    )

    for idx in annotations:
        assert annotations[idx] == baseline_annotations[idx]


def to_annotations_map(annotations: Iterable[Tuple[str, list]]):
    return {key: value for key, value in annotations}
