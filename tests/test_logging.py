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

from rubrix.logging import LoggingMixin


class LoggingForTest(LoggingMixin):
    """class for tests"""

    def __init__(self, a: int = 5):
        self.a = a

    def f(self):
        self.logger.warning("This is an warning %d", self.a)


class LoggingForTestChild(LoggingForTest):
    """class child"""

    pass


def test_logging_mixin_without_breaking_constructors():
    test = LoggingForTest()
    test.f()
    assert test.logger.name == f"{__name__}.{LoggingForTest.__name__}"

    child = LoggingForTestChild(a=10)
    child.f()
    assert child.logger.name == f"{__name__}.{LoggingForTestChild.__name__}"

    assert test.logger != child.logger

    another_child = LoggingForTestChild(a=15)
    # Check logger without call property method
    assert another_child.__getattribute__("__logger__") == child.logger
