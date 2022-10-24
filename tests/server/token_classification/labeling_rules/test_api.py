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

from typing import Any, Dict, List, Optional, Type

from argilla.server.apis.v0.handlers.token_classification_labeling_rules import (
    LabelingRule,
)
from argilla.server.apis.v0.models.token_classification import (
    TokenClassificationRecord,
    TokenClassificationSearchResults,
)
from argilla.server.errors import ServerError, ValidationError
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

    search_by_rule(
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
    )
    search_by_rule(
        client=mocked_client,
        base_url=base_api_url,
        query=rule.query,
        label="OTHER",
    )


def search_by_rule(
    *,
    client,
    base_url: str,
    query: str,
    label: Optional[str] = None,
    send_label: bool = True,
):
    url = f"{base_url}/labeling/rules/{query}/search"
    if label and send_label:
        url += f"?label={label}"

    response = client.get(url)
    data = response.json()
    assert response.status_code == 200, data

    results = TokenClassificationSearchResults.parse_obj(data)
    assert results.aggregations is None
    assert results.total == 4, results

    agent = ServiceLabelingRule.sanitize_query(query)

    def check_when_label(record):
        assert agent in record.annotations
        for entity in record.annotations[agent].entities:
            assert entity.label == label

    def check_when_no_label(record):
        assert agent not in record.annotations

    if label:
        validate = check_when_label
    else:
        validate = check_when_no_label
    for record in results.records:
        validate(record)
    return results


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

    response = client.patch(
        f"{base_url}/labeling/rules/{rule.query}",
        json={
            "description": description or "new Rule description",
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
    assert updated_rule.description == "new Rule description"
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
