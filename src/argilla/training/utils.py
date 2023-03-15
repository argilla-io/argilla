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


def get_default_args(func):
    signature = inspect.signature(func)
    default_args = {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}
    required_args = func.__code__.co_varnames
    for arg in required_args:
        if arg not in default_args:
            default_args[arg] = None
    if "self" in default_args:
        del default_args["self"]
    return default_args


def filter_allowed_args(
    func,
    **kwargs,
):
    allowed_args = {key: val for key, val in kwargs.items() if key in func.__code__.co_varnames}
    if "self" in allowed_args:
        del allowed_args["self"]
    return allowed_args
