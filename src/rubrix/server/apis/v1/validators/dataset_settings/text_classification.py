from fastapi import Depends

from rubrix.server.apis.v1.models.dataset_settings import TextClassificationSettings
from rubrix.server.apis.v1.models.datasets import Dataset
from rubrix.server.apis.v1.validators.dataset_settings.interface import (
    DatasetSettingsValidator,
)
from rubrix.server.daos.records import DatasetRecordsDAO
from rubrix.server.services.metrics import (
    BaseDatasetDB,
    MetricsService,
    TermsAggregation,
)


class TextClassificationDatasetSettingsValidator(DatasetSettingsValidator):
    _INSTANCE = None

    def __init__(self, records: DatasetRecordsDAO, metrics: MetricsService):
        self._records = records
        self._metrics = metrics

    @classmethod
    def get_instance(
        cls,
        records: DatasetRecordsDAO = Depends(DatasetRecordsDAO.get_instance),
        metrics: MetricsService = Depends(MetricsService.get_instance),
    ) -> "TextClassificationDatasetSettingsValidator":
        if not cls._INSTANCE:
            cls._INSTANCE = cls(records, metrics=metrics)
        return cls._INSTANCE

    def validate(self, dataset: Dataset, settings: TextClassificationSettings):
        """
        Validations:
        - check dataset labels against provided settings labels
        """
        return
