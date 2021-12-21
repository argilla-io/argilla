from typing import ClassVar, List

from rubrix.server.tasks.commons.metrics import CommonTasksMetrics
from rubrix.server.tasks.commons.metrics.model.base import BaseMetric, BaseTaskMetrics
from rubrix.server.tasks.text2text import Text2TextRecord


class Text2TextMetrics(BaseTaskMetrics[Text2TextRecord]):
    """
    Configured metrics for text2text task
    """

    metrics: ClassVar[List[BaseMetric]] = CommonTasksMetrics.metrics
