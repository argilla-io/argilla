# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings

try:
    from argilla_v1 import *  # noqa
except ModuleNotFoundError as ex:
    raise Exception(
        'The package argilla-v1 is not installed. Please install it by typing: pip install "argilla[legacy]"',
    ) from ex


def deprecation(message: str):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


deprecation(
    "The module `argilla_sdk.v1` has been include for migration purposes. "
    "It's deprecated and will be removed in the future."
)
