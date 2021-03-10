"""
This module centralizes all configuration and logging management
"""
import logging
from logging import Logger
from typing import Type


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
