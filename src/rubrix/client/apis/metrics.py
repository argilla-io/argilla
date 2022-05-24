from typing import Optional

from rubrix.client.apis import AbstractAPI
from rubrix.client.sdk.datasets.models import TaskType


class MetricsAPI(AbstractAPI):

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
