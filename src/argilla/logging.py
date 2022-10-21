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
from logging import Logger
from typing import Type

try:
    from loguru import logger
except ModuleNotFoundError:
    logger = None


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


class LoguruLoggerHandler(logging.Handler):
    """This logging handler enables an easy way to use loguru fo all built-in logger traces"""

    __LOGLEVEL_MAPPING__ = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    @property
    def is_available(self) -> bool:
        """Return True if handler can tackle log records. False otherwise"""
        return logger is not None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_available:
            self.emit = lambda record: None

    def emit(self, record: logging.LogRecord):

        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.__LOGLEVEL_MAPPING__[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = logger.bind(request_id="argilla")
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logging():

    """Normalizes logging configuration for argilla and its dependencies"""
    intercept_handler = LoguruLoggerHandler()
    if not intercept_handler.is_available:
        return

    logging.basicConfig(handlers=[intercept_handler], level=logging.WARNING)
    for name in logging.root.manager.loggerDict:
        logger_ = logging.getLogger(name)
        logger_.handlers = []

    for name in [
        "uvicorn",
        "uvicorn.lifespan",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "argilla",
        "argilla.server",
    ]:
        logger_ = logging.getLogger(name)
        logger_.propagate = False
        logger_.handlers = [intercept_handler]
