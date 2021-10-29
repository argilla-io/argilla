from typing import Any, Dict

from rubrix.client.sdk.metrics.models import MetricInfo


class MetricResults(MetricInfo):
    results: Dict[str, Any]
