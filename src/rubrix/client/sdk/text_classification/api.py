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
from typing import List, Optional, Union

import httpx

from rubrix.client.sdk.client import AuthenticatedClient
from rubrix.client.sdk.commons.api import (
    build_bulk_response,
    build_data_response,
    build_list_response,
    build_typed_response,
)
from rubrix.client.sdk.commons.models import (
    BulkResponse,
    ErrorMessage,
    HTTPValidationError,
    Response,
)
from rubrix.client.sdk.text_classification.models import (
    LabelingRule,
    LabelingRuleMetricsSummary,
    TextClassificationBulkData,
    TextClassificationQuery,
    TextClassificationRecord,
)


def bulk(
    client: AuthenticatedClient,
    name: str,
    json_body: TextClassificationBulkData,
) -> Response[BulkResponse]:
    url = "{}/api/datasets/{name}/TextClassification:bulk".format(
        client.base_url, name=name
    )

    response = httpx.post(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
        json=json_body.dict(by_alias=True),
    )

    return build_bulk_response(response, name=name, body=json_body)


def data(
    client: AuthenticatedClient,
    name: str,
    request: Optional[TextClassificationQuery] = None,
    limit: Optional[int] = None,
) -> Response[Union[List[TextClassificationRecord], HTTPValidationError, ErrorMessage]]:
    url = "{}/api/datasets/{name}/TextClassification/data".format(
        client.base_url, name=name
    )

    with httpx.stream(
        method="POST",
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=None,
        params={"limit": limit} if limit else None,
        json=request.dict() if request else {},
    ) as response:
        return build_data_response(
            response=response, data_type=TextClassificationRecord
        )


def fetch_dataset_labeling_rules(
    client: AuthenticatedClient,
    name: str,
) -> Response[Union[List[LabelingRule], HTTPValidationError, ErrorMessage]]:

    url = "{}/api/datasets/TextClassification/{name}/labeling/rules".format(
        client.base_url, name=name
    )

    response = httpx.get(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    return build_list_response(response, LabelingRule)


def dataset_rule_metrics(
    client: AuthenticatedClient,
    name: str,
    query: str,
    label: str,
) -> Response[Union[LabelingRuleMetricsSummary, HTTPValidationError, ErrorMessage]]:

    url = "{}/api/datasets/TextClassification/{name}/labeling/rules/{query}/metrics?label={label}".format(
        client.base_url, name=name, query=query, label=label
    )

    response = httpx.get(
        url=url,
        headers=client.get_headers(),
        cookies=client.get_cookies(),
        timeout=client.get_timeout(),
    )

    return build_typed_response(
        response, response_type_class=LabelingRuleMetricsSummary
    )
