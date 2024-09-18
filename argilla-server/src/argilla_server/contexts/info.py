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

import os

import psutil

from argilla_server._version import __version__


def argilla_version() -> str:
    return __version__


def memory_status() -> dict:
    process = psutil.Process(os.getpid())

    return {k: _memory_size(v) for k, v in process.memory_info()._asdict().items()}


def _memory_size(bytes) -> str:
    system = [
        (1024**5, "P"),
        (1024**4, "T"),
        (1024**3, "G"),
        (1024**2, "M"),
        (1024**1, "K"),
        (1024**0, "B"),
    ]

    factor, suffix = None, None
    for factor, suffix in system:
        if bytes >= factor:
            break

    amount = int(bytes / factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple

    return str(amount) + suffix
