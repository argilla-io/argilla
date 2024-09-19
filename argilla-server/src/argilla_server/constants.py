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

API_KEY_HEADER_NAME = "X-Argilla-Api-Key"
WORKSPACE_HEADER_NAME = "X-Argilla-Workspace"

DATABASE_SQLITE = "sqlite"
DATABASE_POSTGRESQL = "postgresql"

SEARCH_ENGINE_ELASTICSEARCH = "elasticsearch"
SEARCH_ENGINE_OPENSEARCH = "opensearch"

DEFAULT_USERNAME = "argilla"
DEFAULT_PASSWORD = "1234"
DEFAULT_API_KEY = "argilla.apikey"

DEFAULT_DATABASE_SQLITE_TIMEOUT = 5

DEFAULT_DATABASE_POSTGRESQL_POOL_SIZE = 15
DEFAULT_DATABASE_POSTGRESQL_MAX_OVERFLOW = 10

DEFAULT_MAX_KEYWORD_LENGTH = 128

# Questions settings defaults
DEFAULT_LABEL_SELECTION_OPTIONS_MAX_ITEMS = 500
DEFAULT_SPAN_OPTIONS_MAX_ITEMS = 500

# The metadata field name prefix defined for protected (non-searchable) values
PROTECTED_METADATA_FIELD_PREFIX = "_"

# Pydantic v2 error: look-around, including look-ahead and look-behind, is not supported so rewriting it:
# ES_INDEX_REGEX_PATTERN = r"^(?!-|_)[a-z0-9-_]+$"
ES_INDEX_REGEX_PATTERN = r"^[a-z0-9][a-z0-9-_]*$"

JS_MAX_SAFE_INTEGER = 9007199254740991
