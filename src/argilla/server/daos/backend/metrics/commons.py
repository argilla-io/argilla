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

from argilla.server.commons.models import TaskStatus
from argilla.server.daos.backend.metrics.base import (
    HistogramAggregation,
    MetadataAggregations,
    TermsAggregation,
    WordCloudAggregation,
)

METRICS = {
    "text_length": HistogramAggregation(
        id="text_length",
        field="metrics.text_length",
        script="params._source.text.length()",
        fixed_interval=1,
    ),
    "error_distribution": TermsAggregation(
        id="error_distribution",
        field="predicted",
        missing="unknown",
        fixed_size=3,
    ),
    "status_distribution": TermsAggregation(
        id="status_distribution",
        field="status",
        fixed_size=len(TaskStatus),
    ),
    "words_cloud": WordCloudAggregation(
        id="words_cloud",
        default_field="text.wordcloud",
    ),
    "metadata": MetadataAggregations(
        id="metadata",
    ),
    "predicted_by": TermsAggregation(
        id="predicted_by",
        field="predicted_by",
    ),
    "annotated_by": TermsAggregation(
        id="annotated_by",
        field="annotated_by",
    ),
    "score": HistogramAggregation(
        id="score",
        field="score",
        fixed_interval=0.001,
    ),
}
