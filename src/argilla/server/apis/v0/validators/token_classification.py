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

from typing import List, Set

from fastapi import Depends

from argilla.server.apis.v0.models.dataset_settings import TokenClassificationSettings
from argilla.server.errors import BadRequestError, EntityNotFoundError
from argilla.server.models import User
from argilla.server.schemas.datasets import Dataset
from argilla.server.services.datasets import DatasetsService
from argilla.server.services.metrics import MetricsService
from argilla.server.services.tasks.token_classification.metrics import DatasetLabels
from argilla.server.services.tasks.token_classification.model import (
    ServiceTokenClassificationAnnotation,
    ServiceTokenClassificationRecord,
)


# TODO(@frascuchon): Move validator and its models to the service layer
class DatasetValidator:
    _INSTANCE = None

    def __init__(self, datasets: DatasetsService, metrics: MetricsService):
        self.__datasets__ = datasets
        self.__metrics__ = metrics

    @classmethod
    def get_instance(
        cls,
        datasets: DatasetsService = Depends(DatasetsService.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ):
        if not cls._INSTANCE:
            cls._INSTANCE = cls(datasets, metrics=metrics)
        return cls._INSTANCE

    async def validate_dataset_settings(self, user: User, dataset: Dataset, settings: TokenClassificationSettings):
        if settings and settings.label_schema:
            results = self.__metrics__.summarize_metric(
                dataset=dataset,
                metric=DatasetLabels(),
                record_class=ServiceTokenClassificationRecord,
                query=None,
            )
            if results:
                labels = results.get("labels", [])
                label_schema = set([label.name for label in settings.label_schema.labels])
                for label in labels:
                    if label not in label_schema:
                        raise BadRequestError(
                            f"The label {label} was found in the dataset but not in provided labels schema. "
                            "\nPlease, provide a valid labels schema according to stored records in the dataset"
                        )

    async def validate_dataset_records(
        self,
        user: User,
        dataset: Dataset,
        records: List[ServiceTokenClassificationRecord],
    ):
        try:
            settings: TokenClassificationSettings = await self.__datasets__.get_settings(
                user=user, dataset=dataset, class_type=TokenClassificationSettings
            )
            if settings and settings.label_schema:
                label_schema = set([label.name for label in settings.label_schema.labels])

                for r in records:
                    if r.prediction:
                        self.__check_label_entities__(label_schema, r.prediction)
                    if r.annotation:
                        self.__check_label_entities__(label_schema, r.annotation)
        except EntityNotFoundError:
            pass

    @staticmethod
    def __check_label_entities__(label_schema: Set[str], annotation: ServiceTokenClassificationAnnotation):
        if not annotation:
            return
        for entity in annotation.entities:
            if entity.label not in label_schema:
                raise BadRequestError(
                    detail=f"Provided records contain the {entity.label} label,"
                    " that is not included in the labels schema."
                    "\nPlease, annotate your records using labels defined in the labels schema."
                )
