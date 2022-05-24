import dataclasses
import logging
import threading
import time
from typing import Callable, List, Optional, Union

import schedule

import rubrix
from rubrix.client import api
from rubrix.client.sdk.commons.errors import NotFoundApiError
from rubrix.listeners.models import (
    ListenerAction,
    ListenerCondition,
    Metrics,
    RBListenerContext,
    Search,
)
from rubrix.metrics.models import MetricSummary


@dataclasses.dataclass
class RBDatasetListener:
    """
    The Rubrix dataset listener class

    Args:
        dataset: The dataset over which listener is created
        action: The action to execute when condition is satisfied
        metrics: A list of metrics ids that will be required in condition
        query: The query string to apply
        condition: The condition to satisfy to execute the action
        query_records: If ``False``, the records won't be passed as argument to the action.
            Default: ``True``
        interval_in_seconds: How often the listener is executed. Default to 30 seconds
    """

    _LOGGER = logging.getLogger(__name__)

    dataset: str
    action: ListenerAction
    metrics: Optional[List[str]] = None
    query: Optional[str] = None
    condition: Optional[ListenerCondition] = None
    query_records: bool = True
    interval_in_seconds: int = 30

    __listener_job__: Optional[schedule.Job] = dataclasses.field(
        init=False, default=None
    )
    __stop_schedule_event__ = None
    __current_thread__ = None
    __scheduler__ = schedule.Scheduler()

    def __post_init__(self):
        self.metrics = self.metrics or []

    def start(self):
        """
        Start listen to changes in the dataset


        If the listener is already started, a ``ValueError`` will be raised

        """
        if self.__listener_job__:
            raise ValueError("Listener is already running")

        self.__listener_job__ = self.__scheduler__.every(
            self.interval_in_seconds
        ).seconds.do(self.__listener_iteration_job__)

        class _ScheduleThread(threading.Thread):
            _WAIT_EVENT = threading.Event()

            @classmethod
            def run(cls):
                while not cls._WAIT_EVENT.is_set():
                    self.__scheduler__.run_pending()
                    time.sleep(self.interval_in_seconds - 1)

            @classmethod
            def stop(cls):
                cls._WAIT_EVENT.set()

        self.__current_thread__ = _ScheduleThread()
        self.__current_thread__.start()

    def stop(self):
        """
        Stops listener if it's still running.

        If listener is already stopped, a ``ValueError`` will be raised

        """
        if not self.__listener_job__:
            raise ValueError("Listener is not running")

        if self.__listener_job__:
            self.__scheduler__.cancel_job(self.__listener_job__)
            self.__listener_job__ = None
            self.__current_thread__.stop()
            self.__current_thread__.join()  # TODO: improve it!

    def __listener_iteration_job__(self):
        """
        Execute a complete listener iteration. The iteration consists on:

        1. Query data and fetch configured metrics
        2. Check search results and metrics with provided condition
        3. Execute the action if condition is satisfied

        """
        current_api = api.active_api()
        try:
            dataset = current_api.datasets.find_by_name(self.dataset)
        except NotFoundApiError:
            self._LOGGER.warning(f"Not found dataset <{self.dataset}>")
            return

        if self.condition is None:
            return self.__run_action__()

        metrics = Metrics()
        for metric in self.metrics:
            metrics.update(
                {
                    metric: current_api.metrics.metric_summary(
                        name=self.dataset, task=dataset.task, metric=metric
                    )
                }
            )
        search_results = current_api.searches.search_records(
            name=self.dataset, task=dataset.task, query=self.query, size=0
        )

        ctx = RBListenerContext(
            listener=self,
            search=Search(total=search_results.total),
            metrics=metrics,
        )
        condition_args = dict(query=ctx.search)
        if metrics:
            condition_args["metrics"] = ctx.metrics
        if self.condition(**condition_args):
            return self.__run_action__(ctx)

    def __run_action__(self, ctx: Optional[RBListenerContext] = None):
        args = [ctx] if ctx else []
        if self.query_records:
            args.insert(
                0, rubrix.load(name=self.dataset, query=self.query, as_pandas=False)
            )
        return self.action(*args)


def listener(
    dataset: str,
    query: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    condition: Optional[Callable[[Union[Search, MetricSummary]], bool]] = None,
    with_records: bool = True,
    execution_interval_in_seconds: int = 30,
):
    """
    Configures the decorated function as a Rubrix listener.

    Args:
        dataset: The dataset name
        query: The query string
        metrics: Required metrics for listener condition
        condition: Defines condition over search and metrics that launch action when is satisfied
        with_records: Include records as part or action arguments. If ``False``,
            only the listener context ``RBListenerContext`` will be passed. Default: ``True``
        execution_interval_in_seconds: Define the execution interval in seconds when listener
            iteration will be executed.

    """

    def inner_decorator(func):
        return RBDatasetListener(
            dataset=dataset,
            action=func,
            condition=condition,
            query=query,
            metrics=metrics,
            query_records=with_records,
            interval_in_seconds=execution_interval_in_seconds,
        )

    return inner_decorator
