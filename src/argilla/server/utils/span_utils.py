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
from typing import Dict, List, Optional, Tuple


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
            ValueError: If a span is invalid, or if a span is not aligned with the tokens.
        """
        not_valid_spans_errors, misaligned_spans_errors = [], []

        for span in spans:
            char_start, char_end = span[1], span[2]
            if char_end - char_start < 1:
                not_valid_spans_errors.append(span)
            elif None in (
                self._start_to_token_idx.get(char_start),
                self._end_to_token_idx.get(char_end),
            ):
                span_str = self.text[char_start:char_end]
                message = f"{span} - {repr(span_str)}"
                misaligned_spans_errors.append(message)

        if not_valid_spans_errors or misaligned_spans_errors:
            message = ""
            if not_valid_spans_errors:
                message += f"Following entity spans are not valid: {not_valid_spans_errors}\n"

            if misaligned_spans_errors:
                spans = "\n".join(misaligned_spans_errors)
                message += "Following entity spans are not aligned with provided tokenization\n"
                message += f"Spans:\n{spans}\n"
                message += f"Tokens:\n{self.tokens}"

            raise ValueError(message)

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
        """Convert IOB or BILOU tags to spans.

        Overlapping spans are NOT supported!

        Args:
            tags: The IOB or BILOU tags.

        Returns:
            A list of spans.

        Raises:
            ValueError: If the list of tags has not the same length as the list of tokens,
                or tags are not in the IOB or BILOU format.
        """

        def get_prefix_and_entity(tag_str: str) -> Tuple[str, Optional[str]]:
            if tag_str == "O":
                return tag_str, None
            splits = tag_str.split("-")
            return splits[0], "-".join(splits[1:])

        if len(tags) != len(self.tokens):
            raise ValueError("The list of tags must have the same length as the list of tokens!")

        spans, start_idx = [], None
        for idx, tag in enumerate(tags):
            prefix, entity = get_prefix_and_entity(tag)

            if prefix == "O":
                continue

            if prefix == "U":
                start_idx, end_idx = self._token_to_char_idx[idx]
                spans.append((entity, start_idx, end_idx))
                start_idx = None
                continue

            if prefix == "L":
                # If no start prefix, we just assume "L" == "U":
                if start_idx is None:
                    start_idx, end_idx = self._token_to_char_idx[idx]
                else:
                    _, end_idx = self._token_to_char_idx[idx]
                spans.append((entity, start_idx, end_idx))
                start_idx = None
                continue

            if prefix == "B":
                start_idx, end_idx = self._token_to_char_idx[idx]
            elif prefix == "I":
                # If "B" is missing, we just assume "I" starts the span
                if start_idx is None:
                    start_idx = self._token_to_char_idx[idx][0]
                end_idx = self._token_to_char_idx[idx][1]
            else:
                raise ValueError("Tags are not in the IOB or BILOU format!")

            try:
                next_tag = tags[idx + 1]
            # Reached last tag, add span
            except IndexError:
                spans.append((entity, start_idx, end_idx))
                break

            next_prefix, next_entity = get_prefix_and_entity(next_tag)
            # span continues
            if next_prefix in ["I", "L"] and next_entity == entity:
                continue
            # span ends
            spans.append((entity, start_idx, end_idx))
            start_idx = None

        return spans
