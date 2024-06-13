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

"""`pydantic.BaseModel`s defined here are shared between `argilla.client.sdk.v1.records`
and `argilla.client.sdk.v1.datasets` modules, so those should be equal, and defined in
`argilla.client.sdk.v1.datasets.models` module instead."""

from argilla_v1.client.sdk.v1.datasets.models import FeedbackItemModel  # noqa: F401
