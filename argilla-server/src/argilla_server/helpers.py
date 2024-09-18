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

"""
Common helper functions
"""

import logging

_LOGGER = logging.getLogger("argilla_server")


def remove_suffix(text: str, suffix: str):
    # TODO Move where is used
    """Give a text, removes suffix substring from it"""
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def replace_string_in_file(filename: str, string: str, replace_by: str, encoding: str = "utf-8"):
    # TODO Move where is used
    """Read a file and replace an old value in file by a new one"""
    # Safely read the input filename using 'with'
    with open(filename, encoding=encoding) as f:
        data = f.read()
        if string not in data:
            return

    # Safely write the changed content, if found in the file
    with open(filename, mode="w", encoding=encoding) as f:
        data = data.replace(string, replace_by)
        f.write(data)
