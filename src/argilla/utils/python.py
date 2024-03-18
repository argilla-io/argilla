import sys
import warnings


def check_deprecated_python_version():
    if sys.version_info < (3, 10):
        warnings.warn(
            category=UserWarning,
            message="Detected a Python version <3.10. The use of this library with Python versions <3.10 is deprecated "
            "and it will be removed in a future version. Please upgrade your Python version to >=3.10.",
        )
