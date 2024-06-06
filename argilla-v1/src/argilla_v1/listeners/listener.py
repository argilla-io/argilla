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

import copy
import dataclasses
import functools
import logging
import threading
import time
from typing import Any, Dict, List, Optional

import schedule

import argilla_v1
from argilla_v1.client import singleton
from argilla_v1.client.sdk.commons.errors import NotFoundApiError
from argilla_v1.listeners.models import ListenerAction, ListenerCondition, Metrics, RGListenerContext, Search


@dataclasses.dataclass
class RGDatasetListener:
    """
    The argilla dataset listener class

    Args:
        dataset: The dataset over which listener is created
        action: The action to execute when the condition is satisfied
        metrics: A list of metrics ids that will be required in condition
        query: The query string to apply
        query_params: Defined parameters used dynamically in the provided query
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
    query_params: Optional[Dict[str, Any]] = None
    condition: Optional[ListenerCondition] = None
    query_records: bool = True
    interval_in_seconds: int = 30

    @property
    def formatted_query(self) -> Optional[str]:
        """Formatted query using defined query params, if any"""
        if self.query is None:
            return None
        return self.query.format(**(self.query_params or {}))

    __listener_job__: Optional[schedule.Job] = dataclasses.field(init=False, default=None)
    __stop_schedule_event__ = None
    __current_thread__ = None
    __scheduler__ = schedule.Scheduler()

    def __post_init__(self):
        self.metrics = self.metrics or []
        self._validate()

    def _validate(self):
        try:
            query = self.formatted_query
            if query:
                self._LOGGER.debug(f"Initial listener query {query}")
        except KeyError as kex:
            raise KeyError("Missing query parameter:", kex)

    def is_running(self):
        """True if listener is running"""
        return self.__listener_job__ is not None

    def __catch_exceptions__(self, cancel_on_failure=False):
        def catch_exceptions_decorator(job_func):
            @functools.wraps(job_func)
            def wrapper(*args, **kwargs):
                try:
                    return job_func(*args, **kwargs)
                except:  # noqa: E722
                    import traceback

                    print(traceback.format_exc())
                    if cancel_on_failure:
                        self.stop()  # We stop the scheduler

            return wrapper

        return catch_exceptions_decorator

    def start(self, *action_args, **action_kwargs):
        """
        Start listen to changes in the dataset. Additionally, args and kwargs can be passed to action
        by using the `action_*` arguments

        If the listener is already started, a ``ValueError`` will be raised

        """
        if self.is_running():
            raise ValueError("Listener is already running")

        job_step = self.__catch_exceptions__(cancel_on_failure=True)(self.__listener_iteration_job__)

        self.__listener_job__ = self.__scheduler__.every(self.interval_in_seconds).seconds.do(
            job_step, *action_args, **action_kwargs
        )

        class _ScheduleThread(threading.Thread):
            _WAIT_EVENT = threading.Event()

            _THREAD_LOGGER = logging.getLogger(__name__)

            @classmethod
            def run(cls):
                cls._THREAD_LOGGER.debug("Running listener thread...")
                while not cls._WAIT_EVENT.is_set():
                    self.__scheduler__.run_pending()
                    time.sleep(self.interval_in_seconds - 1)
                cls._THREAD_LOGGER.debug("Stopping listener thread...")

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
        if not self.is_running():
            raise ValueError("Listener is not running")

        self.__scheduler__.cancel_job(self.__listener_job__)
        self.__listener_job__ = None
        self.__current_thread__.stop()
        self.__current_thread__.join()  # TODO: improve it!

    def __listener_iteration_job__(self, *args, **kwargs):
        """
        Execute a complete listener iteration. The iteration consists on:

        1. Query data and fetch configured metrics
        2. Check search results and metrics with provided condition
        3. Execute the action if condition is satisfied

        """
        current_api = singleton.active_api()
        try:
            dataset = current_api.datasets.find_by_name(self.dataset)
            self._LOGGER.debug(f"Found listener dataset {dataset.name}")
        except NotFoundApiError:
            self._LOGGER.warning(f"Not found dataset <{self.dataset}>")
            return

        ctx = RGListenerContext(
            listener=self,
            query_params=self.query_params,
            metrics=self.__compute_metrics__(current_api, dataset, query=self.formatted_query),
        )
        if self.condition is None:
            self._LOGGER.debug("No condition found! Running action...")
            return self.__run_action__(ctx, *args, **kwargs)

        search_results = current_api.search.search_records(
            name=self.dataset,
            task=dataset.task,
            size=0,
            query_text=self.formatted_query,
        )

        ctx.search = Search(
            total=search_results.total,
            query_params=copy.deepcopy(ctx.query_params),
        )
        condition_args = [ctx.search]
        if self.metrics:
            condition_args.append(ctx.metrics)

        self._LOGGER.debug(f"Evaluate condition with arguments: {condition_args}")
        if self.condition(*condition_args):
            self._LOGGER.debug("Condition passed! Running action...")
            return self.__run_action__(ctx, *args, **kwargs)

    def __compute_metrics__(self, current_api, dataset, query: str) -> Metrics:
        metrics = {}
        for metric in self.metrics:
            metrics.update(
                {
                    metric: current_api.metrics.metric_summary(
                        name=self.dataset,
                        task=dataset.task,
                        metric=metric,
                        query=query,
                    )
                }
            )
        return Metrics(**metrics)

    def __run_action__(self, ctx: Optional[RGListenerContext] = None, *args, **kwargs):
        try:
            action_args = [ctx] if ctx else []
            if self.query_records:
                action_args.insert(0, argilla_v1.load(name=self.dataset, query=self.formatted_query))
            self._LOGGER.debug(f"Running action with arguments: {action_args}")
            return self.action(*args, *action_args, **kwargs)
        except:  # noqa: E722
            import traceback

            print(traceback.format_exc())
            return schedule.CancelJob


def listener(
    dataset: str,
    query: Optional[str] = None,
    metrics: Optional[List[str]] = None,
    condition: Optional[ListenerCondition] = None,
    with_records: bool = True,
    execution_interval_in_seconds: int = 30,
    **query_params,
):
    """
    Configures the decorated function as an argilla listener.

    Args:
        dataset: The dataset name.
        query: The query string.
        metrics: Required metrics for listener condition.
        condition: Defines condition over search and metrics that launch action when is satisfied.
        with_records: Include records as part of action arguments. If ``False``,
            only the listener context ``RGListenerContext`` will be passed. Default: ``True``.
        execution_interval_in_seconds: Define the execution interval in seconds when listener
            iteration will be executed.
        **query_params: Dynamic parameters used in the query. These parameters will be available
            via the listener context and can be updated for subsequent queries.
    """

    def inner_decorator(func):
        return RGDatasetListener(
            dataset=dataset,
            action=func,
            condition=condition,
            query=query,
            query_params=query_params,
            metrics=metrics,
            query_records=with_records,
            interval_in_seconds=execution_interval_in_seconds,
        )

    return inner_decorator
