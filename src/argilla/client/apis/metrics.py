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

from typing import Optional

from argilla.client.apis import AbstractApi
from argilla.client.sdk.datasets.models import TaskType


class MetricsAPI(AbstractApi):

    _API_URL_PATTERN = "/api/datasets/{task}/{name}/metrics/{metric}:summary"

    def metric_summary(
        self,
        name: str,
        task: TaskType,
        metric: str,
        query: Optional[str] = None,
        **metric_params,
    ):
        url = self._API_URL_PATTERN.format(task=task, name=name, metric=metric)
        metric_params = metric_params or {}
        query_params = {k: v for k, v in metric_params.items() if v is not None}
        if query_params:
            url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])

        metric_summary = self.__client__.post(url, json={"query_text": query})
        return metric_summary
