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
from typing import Any, Dict, List, Optional


def unflatten_dict(
    data: Dict[str, Any], sep: str = ".", stop_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
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
