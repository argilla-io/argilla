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

_ES_INDEX_REGEX_PATTERN = r"^(?!-|_)[a-z0-9-_]+$"

API_KEY_HEADER_NAME = "X-Argilla-Api-Key"
WORKSPACE_HEADER_NAME = "X-Argilla-Workspace"

DEFAULT_USERNAME = "argilla"
DEFAULT_PASSWORD = "1234"
DEFAULT_API_URL = "http://localhost:6900"
DEFAULT_API_KEY = "argilla.apikey"
DEFAULT_MAX_KEYWORD_LENGTH = 128

DATASET_NAME_REGEX_PATTERN = _ES_INDEX_REGEX_PATTERN
WORKSPACE_NAME_REGEX_PATTERN = _ES_INDEX_REGEX_PATTERN

# constants for prepare_for_training(framework="openai")
OPENAI_SEPARATOR = "\n\n###\n\n"
OPENAI_END_TOKEN = " END"
OPENAI_WHITESPACE = " "
OPENAI_LEGACY_MODELS = ["babbage", "davinci", "curie", "ada"]
