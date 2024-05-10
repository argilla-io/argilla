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

import inspect
from typing import Dict

args_to_remove = ["self", "cls", "model_args", "args", "kwargs", "model_kwargs"]


def get_default_args(fn) -> dict:
    """
    It takes a function and returns a dictionary of the default arguments

    Args:
      func: The function you want to get the default arguments from.

    Returns:
      A dictionary of the default arguments for the function.
    """
    arg_spec = inspect.getfullargspec(fn)
    # `arg_spec` contains the default values for the optional arguments, starting on the first optional, so there
    # may be mandatory arguments before with no default value, those will be set to `None`, while the rest should match
    # the default values in `arg_spec.defaults`
    default_args = (
        dict(zip(arg_spec.args, [None] * (len(arg_spec.args) - len(arg_spec.defaults)) + list(arg_spec.defaults)))
        if arg_spec.defaults
        else {}
    )
    for key in args_to_remove:
        if key in default_args:
            del default_args[key]
    return default_args


def filter_allowed_args(func, **kwargs):
    """
    It takes a function and a dictionary of arguments, and returns a dictionary of arguments that are
    allowed by the function

    Args:
      func: The function to filter the arguments for.

    Returns:
      A dictionary of the arguments that are allowed in the function.
    """
    allowed_args = {key: val for key, val in kwargs.items() if key in func.__code__.co_varnames}
    for key in args_to_remove:
        if key in allowed_args:
            del allowed_args[key]
    return allowed_args


def _apply_column_mapping(dataset: "Dataset", column_mapping: Dict[str, str]) -> "Dataset":
    """
    Applies the provided column mapping to the dataset, renaming columns accordingly.
    Extra features not in the column mapping are prefixed with `"feat_"`.
    """
    column_mapping = {label_from: label_to for label_to, label_from in column_mapping.items()}
    dataset = dataset.rename_columns(
        {
            **column_mapping,
            **{col: f"feat_{col}" for col in dataset.column_names if col not in column_mapping},
        }
    )
    dset_format = dataset.format
    dataset = dataset.with_format(
        type=dset_format["type"],
        columns=dataset.column_names,
        output_all_columns=dset_format["output_all_columns"],
        **dset_format["format_kwargs"],
    )
    return dataset
