from rubrix.server.apis.v1.models.dataset_settings import AbstractDatasetSettings
from rubrix.server.apis.v1.models.datasets import Dataset


class DatasetSettingsValidator:
    """
    The abstract class definition for the dataset settings validation
    """

    @classmethod
    def get_instance(cls, *args, **kwargs) -> "DatasetSettingsValidator":
        """
            Create a class instance

        Args:
            *args:
            **kwargs:

        Returns:

            An ``DatasetSettingsValidator`` instance
        """
        raise NotImplementedError()

    def validate(self, dataset: Dataset, settings: AbstractDatasetSettings):
        """
        Validate a set of settings for a given dataset. If settings don't pass the validation,
        an validation error should be raised

        Args:
            dataset: The dataset
            settings: The settings to validate
        """
        raise NotImplementedError()


class EmptyDatasetSettingsValidator(DatasetSettingsValidator):
    """
    Noop validator for dataset settings (the default one)
    """

    @classmethod
    def get_instance(cls) -> "DatasetSettingsValidator":
        return cls()

    def validate(self, dataset: Dataset, settings: AbstractDatasetSettings):
        return
