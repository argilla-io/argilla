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

"""
This module centralizes all configuration and logging management
"""

import logging
from logging import Logger, StreamHandler
from typing import Type

try:
    from rich.logging import RichHandler as ArgillaHandler
except ModuleNotFoundError:
    ArgillaHandler = StreamHandler


def full_qualified_class_name(_class: Type) -> str:
    """Calculates the full qualified name (module + class) of a class"""
    class_module = _class.__module__
    if class_module is None or class_module == str.__class__.__module__:
        return _class.__name__  # Avoid reporting __builtin__
    else:
        return f"{class_module}.{_class.__name__}"


def get_logger_for_class(_class: Type) -> Logger:
    """Return the logger for a given class"""
    return logging.getLogger(full_qualified_class_name(_class))


class LoggingMixin:
    """
    Main logging class methods. Classes that inherit from this, have
    available a `logger` properly configured property

    """

    __logger__: Logger = None

    def __new__(cls, *args, **kwargs):
        cls.__logger__ = get_logger_for_class(cls)
        return super().__new__(cls)

    @property
    def logger(self) -> logging.Logger:
        """Return the logger configured for the class"""
        return self.__logger__


def configure_logging():
    """Normalizes logging configuration for argilla and its dependencies"""
    handler = ArgillaHandler()

    # See the note here: https://docs.python.org/3/library/logging.html#logging.Logger.propagate
    # We only attach our handler to the root logger and let propagation take care of the rest
    logging.basicConfig(handlers=[handler], level=logging.WARNING)
