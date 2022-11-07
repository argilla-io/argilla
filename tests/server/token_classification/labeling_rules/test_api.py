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
import math
from typing import Any, Dict, List, Optional, Type

import pytest

from argilla.server.apis.v0.handlers.token_classification_labeling_rules import (
    DatasetLabelingRulesMetricsSummary,
    LabelingRule,
    LabelingRuleSearchResults,
    SearchRecordsByRuleResponse,
)
from argilla.server.apis.v0.models.token_classification import (
    TokenClassificationRecord,
    TokenClassificationSearchResults,
)
from argilla.server.errors import EntityAlreadyExistsError, ServerError, ValidationError
from argilla.server.services.tasks.token_classification.labeling_rules.service import (
    RuleRecordInfo,
)
from argilla.server.services.tasks.token_classification.model import ServiceLabelingRule


def test_rules_creation(mocked_client, records_for_token_classification):
    dataset = "test_rules_creation"
    base_api_url = prepare_dataset(
        client=mocked_client,
        name=dataset,
        records=records_for_token_classification,
    )

    assert_number_of_rules_is(
        client=mocked_client,
        base_url=base_api_url,
        rules=0,
    )
    queries = ["a", "b", "c"]
    for query in queries:
        create_rule(
            client=mocked_client,
            base_url=base_api_url,
            query=query,
        )

    assert_number_of_rules_is(
        client=mocked_client,
        base_url=base_api_url,
        rules=len(queries),
    )


def test_rule_update(mocked_client, records_for_token_classification):

    dataset = "test_rule_update"
    base_api_url = prepare_dataset(
        client=mocked_client,
        name=dataset,
        records=records_for_token_classification,
    )
    rule = create_rule(
        client=mocked_client,
        base_url=base_api_url,
    )

    update_rule(
        client=mocked_client,
        base_url=base_api_url,
        rule=rule,
        name="Wrong name",
        with_error=ValidationError,
        error_detail={
            "detail": {
                "code": "argilla.api.errors::ValidationError",
                "params": {
                    "model": "Request",
                    "errors": [
                        {
                            "loc": ["body", "name"],
                            "msg": 'string does not match regex "^(\\w|[0-9]|_|-|\\.)+$"',
                            "type": "value_error.str.regex",
                            "ctx": {"pattern": "^(\\w|[0-9]|_|-|\\.)+$"},
                        }
                    ],
                },
            }
        },
    )

    rule = update_rule(
        client=mocked_client,
        base_url=base_api_url,
        rule=rule,
        name="better_name",
    )

    rule = update_rule(
        client=mocked_client,
        base_url=base_api_url,
        rule=rule,
        description="New new description HERE!",
        name="better_name",
    )
    other_rule = create_rule(
        client=mocked_client,
        base_url=base_api_url,
        label="LELELE",
        query="peter",
    )
    update_rule(
        client=mocked_client,
        base_url=base_api_url,
        rule=other_rule,
        name="better_name",
        with_error=EntityAlreadyExistsError,
    )
    new_rule = get_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=rule.query,
    )
    assert rule == new_rule


def get_rule(*, client, base_url: str, query: str):
    response = client.get(f"{base_url}/labeling/rules/{query}")
    assert response.status_code == 200
    return LabelingRule.parse_obj(response.json())


def test_delete_rule(mocked_client, records_for_token_classification):
    dataset = "test_rule_update"
    base_api_url = prepare_dataset(
        client=mocked_client,
        name=dataset,
        records=records_for_token_classification,
    )
    rule = create_rule(
        client=mocked_client,
        base_url=base_api_url,
    )
    delete_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=rule.query,
    )

    assert_number_of_rules_is(
        client=mocked_client,
        base_url=base_api_url,
        rules=0,
    )
    delete_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=rule.query,
    )


def test_search_records_by_rule(
    mocked_client,
    records_for_token_classification: List[TokenClassificationRecord],
):
    dataset = "test_rule_update"
    base_api_url = prepare_dataset(
        client=mocked_client,
        name=dataset,
        records=records_for_token_classification,
    )
    query = "b*"
    label = "DD"

    assert_number_of_rules_is(
        client=mocked_client,
        base_url=base_api_url,
        rules=0,
    )

    search_by_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=query,
    )

    results = search_by_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=query,
        label=label,
    )

    rule = create_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=query,
        label=label,
    )

    search_by_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=rule.query,
        label=rule.label,
        send_label=False,
        ids=[results.records[0].id],
    )
    search_by_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=rule.query,
        label="OTHER",
    )


def test_rule_summary(
    mocked_client,
    records_for_token_classification: List[TokenClassificationRecord],
):
    dataset = "test_rule_summary"
    base_api_url = prepare_dataset(
        client=mocked_client,
        name=dataset,
        records=records_for_token_classification,
    )
    query, _ = get_rule_summary(
        client=mocked_client,
        base_url=base_api_url,
    )

    get_rule_summary(
        client=mocked_client,
        base_url=base_api_url,
        label="BB",
        fetch_records=True,
    )

    rule = create_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=query,
    )

    get_rule_summary(
        client=mocked_client,
        base_url=base_api_url,
        label=rule.label,
        fetch_records=True,
        send_label=False,
    )


def test_dataset_rules_summary(
    mocked_client,
    records_for_token_classification: List[TokenClassificationRecord],
):
    dataset = "test_dataset_rules_summary"
    base_api_url = prepare_dataset(
        client=mocked_client,
        name=dataset,
        records=records_for_token_classification,
    )

    results = get_dataset_rules_summary(
        client=mocked_client,
        base_url=base_api_url,
    )

    assert results == DatasetLabelingRulesMetricsSummary(
        coverage=0.0,
        coverage_annotated=0.0,
        total_records=6,
        annotated_records=6,
    )

    create_rule(
        client=mocked_client,
        base_url=base_api_url,
        query="a*",
        label="AA",
    )
    create_rule(
        client=mocked_client,
        base_url=base_api_url,
        query="b*",
        label="BB",
    )

    results = get_dataset_rules_summary(
        client=mocked_client,
        base_url=base_api_url,
    )
    assert results == DatasetLabelingRulesMetricsSummary(
        coverage=4.0,
        coverage_annotated=4.0,
        total_records=6,
        annotated_records=6,
    )


def get_dataset_rules_summary(
    *,
    client,
    base_url: str,
):

    response = client.get(f"{base_url}/labeling/rules/summary")

    data = response.json()
    assert response.status_code == 200, data

    return DatasetLabelingRulesMetricsSummary.parse_obj(data)


def get_rule_summary(
    *,
    client,
    base_url: str,
    label: Optional[str] = None,
    fetch_records: bool = False,
    send_label: bool = True,
):
    query = "a*"
    url = f"{base_url}/labeling/rules/{query}/summary"
    params = {}
    if label and send_label:
        params["label"] = label
    if fetch_records:
        params["with_annotations"] = True
    if params:
        query_params = "&".join([f"{k}={v}" for k, v in params.items()])
        url += f"?{query_params}"

    response = client.get(url)

    data = response.json()
    assert response.status_code == 200, data

    results = LabelingRuleSearchResults.parse_obj(data)
    assert results.dict(exclude={"records"}) == {
        "annotated_records": 6,
        "coverage": 0.6666666666666666,
        "coverage_annotated": 0.6666666666666666,
        "total_records": 6,
    }

    if fetch_records:
        _validate_matched_records(
            records=results.records,
            query=query,
            label=label,
        )

    return query, results


def search_by_rule(
    *,
    client,
    base_url: str,
    query: str,
    label: Optional[str] = None,
    send_label: bool = True,
    ids: List[str] = None,
):
    url = f"{base_url}/labeling/rules/{query}/search"
    if label and send_label:
        url += f"?label={label}"
    response = client.post(url, json={"record_ids": ids or []})
    data = response.json()
    assert response.status_code == 200, data

    results = SearchRecordsByRuleResponse.parse_obj(data)
    assert results.total == len(ids) if ids else 4, results

    _validate_matched_records(
        records=results.records,
        query=query,
        label=label,
    )
    return results


def _validate_matched_records(
    *,
    records: List[RuleRecordInfo],
    query: str,
    label: Optional[str] = None,
):
    def check_when_label(record: RuleRecordInfo):
        assert record.entities

    def check_when_no_label(record: RuleRecordInfo):
        assert not record.entities

    if label:
        validate = check_when_label
    else:
        validate = check_when_no_label

    for r in records:
        validate(r)


def delete_rule(
    *,
    client,
    base_url: str,
    query: str,
):
    response = client.delete(f"{base_url}/labeling/rules/{query}")
    assert response.status_code == 200


def update_rule(
    *,
    client,
    base_url: str,
    rule: LabelingRule,
    description: Optional[str] = None,
    label: Optional[str] = None,
    name: Optional[str] = None,
    with_error: Optional[Type[ServerError]] = None,
    error_detail: Optional[Dict[str, Any]] = None,
):
    description = description or "new Rule description"
    response = client.patch(
        f"{base_url}/labeling/rules/{rule.query}",
        json={
            "description": description,
            "label": label,
            "name": name,
        },
    )
    data = response.json()

    if with_error:
        assert response.status_code == with_error.HTTP_STATUS
        if error_detail:
            assert error_detail == data
        return

    assert response.status_code == 200, data
    updated_rule = LabelingRule.parse_obj(data)
    assert updated_rule.description == description
    assert updated_rule.label == rule.label

    return updated_rule


def create_rule(
    *,
    client,
    base_url: str,
    query: Optional[str] = None,
    label: Optional[str] = None,
) -> LabelingRule:
    response = client.post(
        f"{base_url}/labeling/rules",
        json={
            "query": query or "a*",
            "label": label or "DD",
            "description": "This is a test rule",
        },
    )
    assert response.status_code == 200, response.json()
    return LabelingRule.parse_obj(response.json())


def prepare_dataset(
    *,
    client,
    name: str,
    records: List[TokenClassificationRecord],
):
    client.delete(f"/api/datasets/{name}")
    base_api_url = f"/api/datasets/{name}/TokenClassification"
    assert (
        client.post(
            f"{base_api_url}:bulk",
            json={
                "name": name,
                "records": records,
            },
        ).status_code
        == 200
    )

    return base_api_url


def assert_number_of_rules_is(*, client, base_url, rules: int):
    data = client.get(f"{base_url}/labeling/rules").json()
    assert len(data) == rules
