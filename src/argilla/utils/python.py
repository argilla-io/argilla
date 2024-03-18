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

import sys
import warnings


def check_deprecated_python_version():
    if sys.version_info < (3, 10):
        warnings.warn(
            category=UserWarning,
            message="Detected a Python version <3.10. The use of this library with Python versions <3.10 is deprecated "
            "and it will be removed in a future version. Please upgrade your Python version to >=3.10.",
        )
