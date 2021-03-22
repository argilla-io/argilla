"""
Common helper functions
"""

from typing import Any, Dict, Optional

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


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


def unflatten_dict(data: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """Given a flat dictionary keys, build a hierarchical version by grouping keys"""
    resultDict = {}
    for key, value in data.items():
        parts = key.split(sep)
        d = resultDict
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
    return resultDict


def detect_language(text: str) -> Optional[str]:
    """Return the inferred language code for a given text"""
    try:
        return detect(text)
    except LangDetectException:
        # Cannot detect language for given text. Return None
        # TODO: improve error recovery
        return None
