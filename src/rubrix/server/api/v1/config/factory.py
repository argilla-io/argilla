from rubrix.server.api.v1.models.commons.task import TaskFactory, TaskType
from rubrix.server.api.v1.models.datasets import (
    DatasetUpdate,
    Text2TextDataset,
    Text2TextDatasetCreate,
    TextClassificationDataset,
    TextClassificationDatasetCreate,
    TokenClassificationDataset,
    TokenClassificationDatasetCreate,
)
from rubrix.server.api.v1.models.logging import (
    Text2TextRecord,
    TextClassificationRecord,
    TokenClassificationRecord,
)
from rubrix.server.api.v1.models.weak_supervision import (
    TextClassificationRule,
    TextClassificationRuleCreate,
    TextClassificationRuleUpdate,
)
from rubrix.server.tasks.text2text import Text2TextQuery, Text2TextService
from rubrix.server.tasks.text_classification import (
    TextClassificationQuery,
    TextClassificationService,
)
from rubrix.server.tasks.token_classification import TokenClassificationQuery
from rubrix.server.tasks.token_classification.service.service import (
    TokenClassificationService,
)

__all__ = [
    TaskFactory(
        task=TaskType.text_classification,
        record_class=TextClassificationRecord,
        service_class=TextClassificationService,
        create_dataset_class=TextClassificationDatasetCreate,
        update_dataset_class=DatasetUpdate,
        output_dataset_class=TextClassificationDataset,
        query_class=TextClassificationQuery,
        create_rule_class=TextClassificationRuleCreate,
        update_rule_class=TextClassificationRuleUpdate,
        output_rule_class=TextClassificationRule,
    ),
    TaskFactory(
        task=TaskType.token_classification,
        record_class=TokenClassificationRecord,
        service_class=TokenClassificationService,
        create_dataset_class=TokenClassificationDatasetCreate,
        update_dataset_class=DatasetUpdate,
        output_dataset_class=TokenClassificationDataset,
        query_class=TokenClassificationQuery,
    ),
    TaskFactory(
        task=TaskType.text2text,
        record_class=Text2TextRecord,
        service_class=Text2TextService,
        create_dataset_class=Text2TextDatasetCreate,
        update_dataset_class=DatasetUpdate,
        output_dataset_class=Text2TextDataset,
        query_class=Text2TextQuery,
    ),
]
