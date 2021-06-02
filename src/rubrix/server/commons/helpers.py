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


def limit_value_length(data: Any, max_length: int) -> Any:
    """
    Given an input data, limits string values to a max_length by fetching
    last max_length characters

    Parameters
    ----------
    data:
        Input data
    max_length:
        Max length for string values

    Returns
    -------
        Limited version of data, if any
    """

    if isinstance(data, str):
        return data[-max_length:]
    if isinstance(data, dict):
        return {
            k: limit_value_length(v, max_length=max_length) for k, v in data.items()
        }
    if isinstance(data, (list, tuple, set)):
        new_values = map(lambda x: limit_value_length(x, max_length=max_length), data)
        return type(data)(new_values)
    return data
