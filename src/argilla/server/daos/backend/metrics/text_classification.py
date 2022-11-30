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

from argilla.server.daos.backend.metrics.base import TermsAggregation
from argilla.server.daos.backend.metrics.commons import (
    DatasetLabelingRulesMetric,
    LabelingRulesMetric,
)

METRICS = {
    "predicted_as": TermsAggregation(
        id="predicted_as",
        field="predicted_as",
    ),
    "annotated_as": TermsAggregation(
        id="annotated_as",
        field="annotated_as",
    ),
    "labeling_rule": LabelingRulesMetric(id="labeling_rule"),
    "dataset_labeling_rules": DatasetLabelingRulesMetric(id="dataset_labeling_rules"),
}
