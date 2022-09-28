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

from typing import Any, Dict, Optional, Type

from fastapi import Depends

from argilla.server.daos.models.records import DaoRecordsSearch
from argilla.server.daos.records import DatasetRecordsDAO
from argilla.server.services.datasets import ServiceDataset
from argilla.server.services.metrics.models import ServiceMetric, ServicePythonMetric
from argilla.server.services.search.model import ServiceRecordsQuery
from argilla.server.services.tasks.commons import ServiceRecord


class MetricsService:
    """The dataset metrics service singleton"""

    _INSTANCE = None

    @classmethod
    def get_instance(
        cls,
        dao: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
    ) -> "MetricsService":
        """
        Creates the service instance.

        Parameters
        ----------
        dao:
            The dataset records dao

        Returns
        -------
            The metrics service instance

        """
        if not cls._INSTANCE:
            cls._INSTANCE = cls(dao)
        return cls._INSTANCE

    def __init__(self, dao: DatasetRecordsDAO):
        """
        Creates a service instance

        Parameters
        ----------
        dao:
            The dataset records dao
        """
        self.__dao__ = dao

    def summarize_metric(
        self,
        dataset: ServiceDataset,
        metric: ServiceMetric,
        record_class: Optional[Type[ServiceRecord]] = None,
        query: Optional[ServiceRecordsQuery] = None,
        **metric_params,
    ) -> Dict[str, Any]:
        """
        Applies a metric summarization.

        Parameters
        ----------
        dataset:
            The records dataset
        metric:
            The selected metric
        record_class:
            The record class type for python metrics computation
        query:
            An optional query passed for records filtering
        metric_params:
            Related metrics parameters

        Returns
        -------
            The metric summarization info
        """

        if isinstance(metric, ServicePythonMetric):
            records = self.__dao__.scan_dataset(
                dataset, search=DaoRecordsSearch(query=query)
            )
            return metric.apply(map(record_class.parse_obj, records))

        return self.__dao__.compute_metric(
            metric_id=metric.id,
            metric_params=metric_params,
            dataset=dataset,
            query=query,
        )
