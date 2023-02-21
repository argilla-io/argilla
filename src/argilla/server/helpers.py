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
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger("argilla.server")


def unflatten_dict(data: Dict[str, Any], sep: str = ".", stop_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Given a flat dictionary keys, build a hierarchical version by grouping keys

    Parameters
    ----------
    data:
        The data dictionary
    sep:
        The key separator. Default "."
    stop_keys
        List of dictionary first level keys where hierarchy will stop

    Returns
    -------

    """
    resultDict = {}
    stop_keys = stop_keys or []
    for key, value in data.items():
        if key is not None:
            parts = key.split(sep)
            if parts[0] in stop_keys:
                parts = [parts[0], sep.join(parts[1:])]
            d = resultDict
            for part in parts[:-1]:
                if part not in d:
                    d[part] = {}
                d = d[part]
            d[parts[-1]] = value
    return resultDict


def flatten_dict(data: Dict[str, Any], sep: str = ".", drop_empty: bool = False) -> Dict[str, Any]:
    """
    Flatten a data dictionary

    Parameters
    ----------
    data:
        The data dictionary
    sep:
        The generated key separator. Default="."
    drop_empty:
        If true, keys with empty lists or None values will be omitted

    Returns
    -------

        A flattened key dictionary
    """

    def _is_empty_value(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        return False

    def _flatten_internal_(_data: Dict[str, Any], _parent_key="", _sep="."):
        items = []
        for key, value in _data.items():
            if drop_empty and _is_empty_value(value):
                continue

            new_key = _parent_key + _sep + key if _parent_key else key
            try:
                items.extend(_flatten_internal_(value, new_key, _sep=_sep).items())
            except Exception:
                items.append((new_key, value))
        return dict(items)

    return _flatten_internal_(data, _sep=sep)


def takeuntil(iterable, limit: int):
    """
    Iterate over inner iterable until a count limit

    Parameters
    ----------
    iterable:
        The inner iterable
    limit:
        The limit

    Returns
    -------

    """
    count = 0
    for e in iterable:
        if count < limit:
            yield e
            count += 1
        else:
            break


def remove_prefix(text: str, prefix: str):
    """Give a text, removes prefix substring from it"""
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def remove_suffix(text: str, suffix: str):
    """Give a text, removes suffix substring from it"""
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text


def replace_string_in_file(
    filename: str,
    string: str,
    replace_by: str,
    encoding: str = "utf-8",
):
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
