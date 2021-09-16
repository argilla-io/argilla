#  coding=utf-8
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

""" Contains all the data models used in inputs/outputs """

from .api_info import ApiInfo
from .api_status import ApiStatus
from .api_status_elasticsearch import ApiStatusElasticsearch
from .api_status_mem_info import ApiStatusMemInfo
from .bulk_response import BulkResponse
from .class_prediction import ClassPrediction
from .dataset import Dataset
from .dataset_metadata import DatasetMetadata
from .dataset_tags import DatasetTags
from .entity_span import EntitySpan
from .error_message import ErrorMessage
from .http_validation_error import HTTPValidationError
from .prediction_status import PredictionStatus
from .task_status import TaskStatus
from .task_type import TaskType
from .text_classification_annotation import TextClassificationAnnotation
from .text_classification_bulk_data import TextClassificationBulkData
from .text_classification_bulk_data_metadata import TextClassificationBulkDataMetadata
from .text_classification_bulk_data_tags import TextClassificationBulkDataTags
from .text_classification_query import TextClassificationQuery
from .text_classification_query_metadata import TextClassificationQueryMetadata
from .text_classification_record import TextClassificationRecord
from .text_classification_record_explanation import TextClassificationRecordExplanation
from .text_classification_record_inputs import TextClassificationRecordInputs
from .text_classification_record_metadata import TextClassificationRecordMetadata
from .text_classification_search_request import TextClassificationSearchRequest
from .text_classification_search_results import TextClassificationSearchResults
from .token_attributions import TokenAttributions
from .token_attributions_attributions import TokenAttributionsAttributions
from .token_classification_aggregations import TokenClassificationAggregations
from .token_classification_aggregations_annotated_as import (
    TokenClassificationAggregationsAnnotatedAs,
)
from .token_classification_aggregations_annotated_by import (
    TokenClassificationAggregationsAnnotatedBy,
)
from .token_classification_aggregations_metadata import (
    TokenClassificationAggregationsMetadata,
)
from .token_classification_aggregations_metadata_additional_property import (
    TokenClassificationAggregationsMetadataAdditionalProperty,
)
from .token_classification_aggregations_predicted import (
    TokenClassificationAggregationsPredicted,
)
from .token_classification_aggregations_predicted_as import (
    TokenClassificationAggregationsPredictedAs,
)
from .token_classification_aggregations_predicted_by import (
    TokenClassificationAggregationsPredictedBy,
)
from .token_classification_aggregations_status import (
    TokenClassificationAggregationsStatus,
)
from .token_classification_aggregations_words import (
    TokenClassificationAggregationsWords,
)
from .token_classification_annotation import TokenClassificationAnnotation
from .token_classification_bulk_data import TokenClassificationBulkData
from .token_classification_bulk_data_metadata import TokenClassificationBulkDataMetadata
from .token_classification_bulk_data_tags import TokenClassificationBulkDataTags
from .token_classification_query import TokenClassificationQuery
from .token_classification_query_metadata import TokenClassificationQueryMetadata
from .token_classification_record import TokenClassificationRecord
from .token_classification_record_metadata import TokenClassificationRecordMetadata
from .token_classification_search_request import TokenClassificationSearchRequest
from .token_classification_search_results import TokenClassificationSearchResults
from .update_dataset_request import UpdateDatasetRequest
from .update_dataset_request_metadata import UpdateDatasetRequestMetadata
from .update_dataset_request_tags import UpdateDatasetRequestTags
from .user import User
from .validation_error import ValidationError
