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

from dataclasses import dataclass
from typing import Any, Dict

import pytest
from argilla_v1.client.feedback.integrations.huggingface.model_card.model_card import (
    _prepare_dict_for_comparison,
    _updated_arguments,
)
from argilla_v1.training.utils import get_default_args
from transformers import TrainingArguments

default_transformer_args = get_default_args(TrainingArguments.__init__)
default_transformer_args_1 = default_transformer_args.copy()
default_transformer_args_1.update({"output_dir": None, "warmup_steps": 100})
default_transformer_args_2 = default_transformer_args.copy()
default_transformer_args_2.update({"output_dir": {"nested_name": "test"}})
default_transformer_args_3 = default_transformer_args.copy()
default_transformer_args_3.update({"output_dir": [1.2, 3, "value"]})


@dataclass
class Dummy:
    # Test a random class, it could be a loss function passed as a callable, or an instance
    # of one for example.
    pass


default_transformer_args_4 = default_transformer_args.copy()
default_transformer_args_4.update({"output_dir": Dummy, "other": Dummy()})


@pytest.mark.parametrize(
    "current_kwargs, new_kwargs",
    (
        (default_transformer_args_1, {"warmup_steps": 100}),
        (default_transformer_args_2, {"output_dir": {"nested_name": "test"}}),
        (default_transformer_args_3, {"output_dir": [1.2, 3, "value"]}),
        (default_transformer_args_4, {"output_dir": Dummy, "other": Dummy()}),
    ),
)
def test_updated_kwargs(current_kwargs: Dict[str, Any], new_kwargs: Dict[str, Any]):
    # Using only the Transformer's TrainingArguments as an example, no need to check if the arguments are correct

    new_arguments = _updated_arguments(default_transformer_args, current_kwargs)
    assert set(_prepare_dict_for_comparison(new_arguments).items()) == set(
        _prepare_dict_for_comparison(new_kwargs).items()
    )
