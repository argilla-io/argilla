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
from typing import List, Union

from argilla.client.feedback.schemas.enums import FieldTypes, MetadataPropertyTypes
from argilla.pydantic_v1 import StrictFloat, StrictInt, StrictStr

FETCHING_BATCH_SIZE = 250
PUSHING_BATCH_SIZE = 32
DELETE_DATASET_RECORDS_MAX_NUMBER = 100

FIELD_TYPE_TO_PYTHON_TYPE = {FieldTypes.text: str}
