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

import logging
import sys

from argilla.logging import ArgillaHandler
from argilla.utils import LazyargillaModule


def test_lazy_module():
    assert isinstance(sys.modules["argilla"], LazyargillaModule)


def test_configure_logging_call():
    # Ensure that the root logger uses the ArgillaHandler (RichHandler if rich is installed),
    # whereas the other loggers do not have handlers
    assert isinstance(logging.getLogger().handlers[0], ArgillaHandler)
    assert len(logging.getLogger("argilla").handlers) == 0
