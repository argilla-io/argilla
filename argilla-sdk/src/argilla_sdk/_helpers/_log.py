# Copyright 2024-present, Argilla, Inc.
# TODO: This license is not consistent with the license used in the project.
#       Delete the inconsistent license and above line and rerun pre-commit to insert a good license.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging

LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def log(message: str, level: str = "info") -> None:
    """Log a message at the specified level.
    Args:
        message (str): The message to log.
        level (str): The log level to use. Defaults to "info".
    """
    level_int = LOG_LEVEL_MAP.get(level, logging.INFO)
    logging.log(level=level_int, msg=message)
