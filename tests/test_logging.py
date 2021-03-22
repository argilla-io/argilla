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
