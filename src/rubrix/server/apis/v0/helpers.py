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
from typing import Any, Dict


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


def flatten_dict(
    data: Dict[str, Any], sep: str = ".", drop_empty: bool = False
) -> Dict[str, Any]:
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
