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
try:
    from argilla.server.server import app
except ModuleNotFoundError as ex:
    _module_name = ex.name

    def fallback_app(*args, **kwargs):
        raise RuntimeError(
            "\n"
            f"Cannot start argilla server. Some dependencies were not found:[{_module_name}].\n"
            "Please, install missing modules or reinstall argilla with server extra deps:\n"
            "pip install argilla[server]"
        )

    app = fallback_app
