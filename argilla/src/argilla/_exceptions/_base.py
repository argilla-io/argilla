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


class ArgillaErrorBase(Exception):
    message_stub = "Argilla SDK error"
    message: str = message_stub

    def __init__(self, message: str = message, status_code: int = 500):
        """Base class for all Argilla exceptions
        Args:
            message (str): The message to display when the exception is raised
            status_code (int): The status code of the response that caused the exception
        """
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        return f"{self.message_stub}: {self.__class__.__name__}: {super().__str__()}"

    def __repr__(self):
        return f"{self.message_stub}: {self.__class__.__name__}: {super().__repr__()}"
