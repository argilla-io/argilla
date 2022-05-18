from typing import List, Optional, Set, Type

from fastapi import Depends

from rubrix.server.apis.v0.models.commons.model import TaskType
from rubrix.server.apis.v0.models.dataset_settings import TextClassificationSettings
from rubrix.server.apis.v0.models.datasets import Dataset
from rubrix.server.apis.v0.models.metrics.text_classification import DatasetLabels
from rubrix.server.apis.v0.models.text_classification import (
    CreationTextClassificationRecord,
    TextClassificationRecord,
)
from rubrix.server.errors import BadRequestError, EntityNotFoundError
from rubrix.server.security.model import User
from rubrix.server.services.datasets import DatasetsService, SVCDatasetSettings

__svc_settings_class__: Type[SVCDatasetSettings] = type(
    f"{TaskType.text_classification}_DatasetSettings",
    (SVCDatasetSettings, TextClassificationSettings),
    {},
)

from rubrix.server.services.metrics import MetricsService


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

    async def validate_dataset_settings(
        self, user: User, dataset: Dataset, settings: TextClassificationSettings
    ):
        if settings and settings.label_schema:
            results = self.__metrics__.summarize_metric(
                dataset=dataset,
                metric=DatasetLabels(),
                record_class=TextClassificationRecord,
                query=None,
            )
            if results:
                labels = results.get("labels", [])
                label_schema = set(
                    [label.name for label in settings.label_schema.labels]
                )
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
        records: Optional[List[CreationTextClassificationRecord]] = None,
    ):
        try:
            settings: TextClassificationSettings = await self.__datasets__.get_settings(
                user=user, dataset=dataset, class_type=__svc_settings_class__
            )
            if settings and settings.label_schema:
                label_schema = set(
                    [label.name for label in settings.label_schema.labels]
                )
                for r in records:
                    if r.prediction:
                        self.__check_label_classes__(
                            label_schema,
                            [label.class_label for label in r.prediction.labels],
                        )
                    if r.annotation:
                        self.__check_label_classes__(
                            label_schema,
                            [label.class_label for label in r.annotation.labels],
                        )
        except EntityNotFoundError:
            pass

    @staticmethod
    def __check_label_classes__(
        label_schema: Set[str],
        labels: List[str],
    ):
        for label in labels:
            if label not in label_schema:
                raise BadRequestError(
                    detail=f"Provided records contain the {label} label,"
                    " that is not included in the labels schema."
                    "\nPlease, annotate your records using labels defined in the labels schema."
                )
