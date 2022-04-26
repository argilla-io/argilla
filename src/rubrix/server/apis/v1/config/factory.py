from rubrix.server.apis.v1.models.commons.task import TaskType
from rubrix.server.apis.v1.models.commons.task_factory import TaskFactory
from rubrix.server.apis.v1.models.dataset_settings import TextClassificationSettings
from rubrix.server.elasticseach.mappings.text2text import text2text_mappings
from rubrix.server.elasticseach.mappings.text_classification import (
    text_classification_mappings,
)
from rubrix.server.elasticseach.mappings.token_classification import (
    token_classification_mappings,
)

__all__ = [
    TaskFactory(
        task=TaskType.text_classification,
        settings_class=TextClassificationSettings,
        es_mapping=text_classification_mappings(),
    ),
    TaskFactory(
        task=TaskType.token_classification,
        es_mapping=token_classification_mappings(),
    ),
    TaskFactory(
        task=TaskType.text2text,
        es_mapping=text2text_mappings(),
    ),
]


def find_config_by_task(task: TaskType) -> TaskFactory:
    """
    Finds task factory configuration for a given task

    Args:
        task: The task type

    Returns:
        The related task factory configuration for given task
    """
    for cfg in __all__:
        if cfg.task == task:
            return cfg
    raise RuntimeError(f"Not found info for task '{task}'")
