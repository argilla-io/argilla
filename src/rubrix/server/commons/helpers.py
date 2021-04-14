"""
Common helper functions
"""

from typing import Any, Dict, List, Optional


def flatten_dict(data: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """
    Flatten a data dictionary

    Parameters
    ----------
    data:
        The data dictionary
    sep:
        The generated key separator. Default="."

    Returns
    -------

        A flattened key dictionary
    """

    def _flatten_internal_(_data: Dict[str, Any], _parent_key="", _sep="."):
        items = []
        for key, value in _data.items():
            new_key = _parent_key + _sep + key if _parent_key else key
            try:
                items.extend(_flatten_internal_(value, new_key, _sep=_sep).items())
            except Exception:
                items.append((new_key, value))
        return dict(items)

    return _flatten_internal_(data, _sep=sep)


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

    for key, value in data.items():
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
