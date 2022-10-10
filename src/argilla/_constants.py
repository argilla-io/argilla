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

MAX_KEYWORD_LENGTH = 128


API_KEY_HEADER_NAME = "X-Argilla-Api-Key"
WORKSPACE_HEADER_NAME = "X-Argilla-Workspace"
DEFAULT_API_KEY = "rubrix.apikey"  # Keep the same api key for now

_OLD_API_KEY_HEADER_NAME = "X-Rubrix-Api-Key"
_OLD_WORKSPACE_HEADER_NAME = "X-Rubrix-Workspace"

DATASET_NAME_REGEX_PATTERN = r"^(?!-|_)[a-z0-9-_]+$"
