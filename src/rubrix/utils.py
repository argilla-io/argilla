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
import asyncio
import importlib
import os
import threading
import warnings
from collections import defaultdict
from itertools import chain
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple


class _LazyRubrixModule(ModuleType):
    """Module class that surfaces all objects but only performs associated imports when the objects are requested.

    Shamelessly copied and adapted from the Hugging Face transformers implementation.
    """

    def __init__(
        self,
        name,
        module_file,
        import_structure,
        deprecated_import_structure=None,
        module_spec=None,
        extra_objects=None,
    ):
        super().__init__(name)
        self._modules = set(import_structure.keys())
        self._class_to_module = {}
        for key, values in import_structure.items():
            for value in values:
                self._class_to_module[value] = key
        # Needed for autocompletion in an IDE
        self.__all__ = list(import_structure.keys()) + list(
            chain(*import_structure.values())
        )
        self.__file__ = module_file
        self.__spec__ = module_spec
        self.__path__ = [os.path.dirname(module_file)]
        self._objects = {} if extra_objects is None else extra_objects
        self._name = name
        self._import_structure = import_structure

        # deprecated stuff
        deprecated_import_structure = deprecated_import_structure or {}
        self._deprecated_modules = set(deprecated_import_structure.keys())
        self._deprecated_class_to_module = {}
        for key, values in deprecated_import_structure.items():
            for value in values:
                self._deprecated_class_to_module[value] = key

    # Needed for autocompletion in an IDE
    def __dir__(self):
        result = super().__dir__()
        # The elements of self.__all__ that are submodules may or may not be in the dir already, depending on whether
        # they have been accessed or not. So we only add the elements of self.__all__ that are not already in the dir.
        for attr in self.__all__:
            if attr not in result:
                result.append(attr)
        return result

    def __getattr__(self, name: str) -> Any:
        if name in self._objects:
            return self._objects[name]
        if name in self._modules:
            value = self._get_module(name)
        elif name in self._class_to_module.keys():
            module = self._get_module(self._class_to_module[name])
            value = getattr(module, name)
        elif name in self._deprecated_modules:
            value = self._get_module(name, deprecated=True)
        elif name in self._deprecated_class_to_module.keys():
            module = self._get_module(
                self._deprecated_class_to_module[name], deprecated=True, class_name=name
            )
            value = getattr(module, name)
        else:
            raise AttributeError(f"module {self.__name__} has no attribute {name}")

        setattr(self, name, value)
        return value

    def _get_module(
        self,
        module_name: str,
        deprecated: bool = False,
        class_name: Optional[str] = None,
    ):
        if deprecated:
            warnings.warn(
                f"Importing '{class_name or module_name}' from the rubrix namespace (that is "
                f"`rubrix.{class_name or module_name}`) is deprecated and will not work in a future version. "
                f"Make sure you update your code accordingly.",
                category=FutureWarning,
            )

        try:
            return importlib.import_module("." + module_name, self.__name__)
        except Exception as e:
            raise RuntimeError(
                f"Failed to import {self.__name__}.{module_name} because of the following error "
                f"(look up to see its traceback):\n{e}"
            ) from e

    def __reduce__(self):
        return self.__class__, (self._name, self.__file__, self._import_structure)


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


def setup_loop_in_thread() -> Tuple[asyncio.AbstractEventLoop, threading.Thread]:
    """Sets up a new asyncio event loop in a new thread, and runs it forever.

    Returns:
        A tuple containing the event loop and the thread.
    """
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()

    return loop, thread


class SpanUtils:
    """Holds utility methods to work with a tokenized text and entity spans.

    Spans must be tuples containing the label (str), start char idx (int), and end char idx (int).

    Args:
        text: The text the spans refer to.
        tokens: The tokens of the text.
    """

    def __init__(self, text: str, tokens: List[str]):
        self._text, self._tokens = text, tokens

        self._token_to_char_idx: Dict[int, Tuple[int, int]] = {}
        self._start_to_token_idx: Dict[int, int] = {}
        self._end_to_token_idx: Dict[int, int] = {}
        self._char_to_token_idx: Dict[int, int] = {}

        end_idx = 0
        for idx, token in enumerate(tokens):
            start_idx = text.find(token, end_idx)
            if start_idx == -1:
                raise ValueError(f"Token '{token}' not found in text: {text}")
            end_idx = start_idx + len(token)

            self._token_to_char_idx[idx] = (start_idx, end_idx)
            self._start_to_token_idx[start_idx] = idx
            self._end_to_token_idx[end_idx] = idx
            for i in range(start_idx, end_idx):
                self._char_to_token_idx[i] = idx

            # convention: skip first white space after a token
            try:
                if text[end_idx] == " ":
                    end_idx += 1
            # reached end of text
            except IndexError:
                pass

    @property
    def text(self) -> str:
        """The text the spans refer to."""
        return self._text

    @property
    def tokens(self) -> List[str]:
        """The tokens of the text."""
        return self._tokens

    @property
    def token_to_char_idx(self) -> Dict[int, Tuple[int, int]]:
        """The token index to start/end char index mapping."""
        return self._token_to_char_idx

    @property
    def char_to_token_idx(self) -> Dict[int, int]:
        """The char index to token index mapping."""
        return self._char_to_token_idx

    def validate(self, spans: List[Tuple[str, int, int]]):
        """Validates the alignment of span boundaries and tokens.

        Args:
            spans: A list of spans.

        Raises:
            ValueError: If one or more spans are not aligned with the tokens.
        """
        misaligned_spans = []
        for span in spans:
            if None in (
                self._start_to_token_idx.get(span[1]),
                self._end_to_token_idx.get(span[2]),
            ):
                misaligned_spans.append(self.text[span[1] : span[2]])

        if misaligned_spans:
            raise ValueError(
                f"The entity spans {misaligned_spans} are not aligned with following tokens: {self.tokens}"
            )

    def correct(self, spans: List[Tuple[str, int, int]]) -> List[Tuple[str, int, int]]:
        """Correct span boundaries for leading/trailing white spaces, new lines and tabs.

        Args:
            spans: Spans to be corrected.

        Returns:
            The corrected spans.
        """
        corrected_spans = []
        for span in spans:
            start, end = span[1], span[2]

            if start < 0:
                start = 0
            if end > len(self.text):
                end = len(self.text)

            while start <= len(self.text) and not self.text[start].strip():
                start += 1
            while not self.text[end - 1].strip():
                end -= 1

            corrected_spans.append((span[0], start, end))

        return corrected_spans

    def to_tags(self, spans: List[Tuple[str, int, int]]) -> List[str]:
        """Convert spans to IOB tags.

        Args:
            spans: Spans to transform into IOB tags.

        Returns:
            The IOB tags.

        Raises:
            ValueError: If spans overlap, the IOB format does not support overlapping spans.
        """
        # check for overlapping spans
        sorted_spans = sorted(spans, key=lambda x: x[1])
        for i in range(1, len(spans)):
            if sorted_spans[i - 1][2] > sorted_spans[i][1]:
                raise ValueError("IOB tags cannot handle overlapping spans!")

        tags = ["O"] * len(self.tokens)
        for span in spans:
            start_token_idx = self._start_to_token_idx[span[1]]
            end_token_idx = self._end_to_token_idx[span[2]]

            tags[start_token_idx] = f"B-{span[0]}"
            for token_idx in range(start_token_idx + 1, end_token_idx + 1):
                tags[token_idx] = f"I-{span[0]}"

        return tags

    def from_tags(self, tags: List[str]) -> List[Tuple[str, int, int]]:
        """Convert IOB tags to spans.

        Args:
            tags: The IOB tags.

        Returns:
            A list of spans.

        Raises:
            ValueError: If the list of tags has not the same length as the list of tokens.
            TypeError: If tags are not in the IOB format.
        """

        def get_prefix_and_entity(tag_str: str) -> Tuple[str, Optional[str]]:
            if tag_str == "O":
                return tag_str, None
            splits = tag_str.split("-")
            return splits[0], "-".join(splits[1:])

        if len(tags) != len(self.tokens):
            raise ValueError(
                "The list of tags must have the same length as the list of tokens!"
            )

        spans, start_idx = [], None
        for idx, tag in enumerate(tags):
            prefix, entity = get_prefix_and_entity(tag)

            if prefix == "O":
                continue

            if prefix == "B":
                start_idx, end_idx = self._token_to_char_idx[idx]
            elif prefix == "I":
                # If B is missing we just assume I starts the span
                if start_idx is None:
                    start_idx = self._token_to_char_idx[idx][0]
                end_idx = self._token_to_char_idx[idx][1]
            else:
                raise TypeError("Tags are not in the IOB format!")

            try:
                next_tag = tags[idx + 1]
            # Reached last tag, add span
            except IndexError:
                spans.append((entity, start_idx, end_idx))
                break

            next_prefix, next_entity = get_prefix_and_entity(next_tag)
            # span continues
            if next_prefix == "I" and next_entity == entity:
                continue
            # span ends
            spans.append((entity, start_idx, end_idx))
            start_idx = None

        return spans
