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

from typing import Dict, List, Tuple, Union

from argilla.pydantic_v1 import BaseModel


class TextClassificationReturnTypes(BaseModel):
    """
    Union[
        Tuple[str, str],
        Tuple[str, List[str]],
        List[Tuple[str, str]],
        List[Tuple[str, List[str]]]
    ]
    """

    format: Union[
        Tuple[str, Union[str, int]],
        Tuple[str, List[Union[str, int]]],
        List[Tuple[str, Union[str, int]]],
        List[Tuple[str, List[Union[str, int]]]],
    ]


class SFTReturnTypes(BaseModel):
    """
    Union[
        str,
        List[str]
    ]
    """

    format: Union[str, List[str]]


class RMReturnTypes(BaseModel):
    """
    Union[
        Tuple[str, str],
        Tuple[str, List[str]],
        List[Tuple[str, str]],
        List[Tuple[str, List[str]]]
    ]
    """

    format: Union[Tuple[str, str], Tuple[str, List[str]], List[Tuple[str, str]], List[Tuple[str, List[str]]]]


class PPOReturnTypes(BaseModel):
    """
    Union[
        str,
        List[str]
    ]
    """

    format: Union[str, List[str]]


class DPOReturnTypes(BaseModel):
    """
    Union
        Tuple[str, str, str],
        List[Tuple[str, str, str]]
    ]
    """

    format: Union[Tuple[str, str, str], List[Tuple[str, str, str]]]


class QuestionAnsweringReturnTypes(BaseModel):
    """
    Union[
        Tuple[str, str, str],
        List[Tuple[str, str, str]]
    ]
    """

    format: Union[Tuple[str, str, str], List[Tuple[str, str, str]]]


class ChatCompletionReturnTypes(BaseModel):
    """
    Union[
        Tuple[str, str, str, str],
        List[Tuple[str, str, str, str]]
    ]
    """

    format: Union[Tuple[str, str, str, str], List[Tuple[str, str, str, str]]]


class SentenceSimilarityReturnTypes(BaseModel):
    r"""
    Union[
        Dict[str, Union[float, int, str]],  # case 1 with with two string elements and one int/float, case 3 with one or three strings and one int/float.
        List[Dict[str, Union[float, int, str]]],  # case 1 with with two string elements and one int/float, case 3 with one or three strings and one int/float.
    ]

    For a reference of the different cases take a look at:
    https://huggingface.co/blog/how-to-train-sentence-transformers#how-to-prepare-your-dataset-for-training-a-sentence-transformers-model
    """

    format: Union[Dict[str, Union[float, int, str]], List[Dict[str, Union[float, int, str]]]]
