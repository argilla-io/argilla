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
# Remove me
import warnings

from argilla_server.pydantic_v1 import PYDANTIC_MAJOR_VERSION

if PYDANTIC_MAJOR_VERSION >= 2:
    warnings.warn("The argilla_server package is not compatible with Pydantic 2. " "Please use Pydantic 1.x instead.")
else:
    from argilla_server._app import app  # noqa
