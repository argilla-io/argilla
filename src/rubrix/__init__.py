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

"""This file reflects the user facing API.
If you want to add something here, remember to add it as normal import in the _TYPE_CHECKING section (for IDEs),
as well as in the `_import_structure` dictionary.
"""
import inspect

from . import _version, _version

__version__ = _version.version


message = """
    The rubrix package name has changed its name to argilla. 
    
    This is the last version of rubrix and the argilla package 
    has been installed for your convenience. You need to use: 
    
    import argilla
    
    and launch the server with:
    
    $>python -m argilla
    \t 
"""


print(inspect.cleandoc(message))
