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

import textwrap


def text_wrapper(self, attr_ignore: list = None, attr_multiline: list = None):
    """
    This is a general function that creates __repr__ methods for classes that inherit from pydantic.BaseModel.

    Args:
        self: The class that inherits from pydantic.BaseModel.
        attr_ignore: A list of attributes that should be ignored in the __repr__ method.
        attr_multiline: A list of attributes that should be printed in multiple lines in the __repr__ method. The attribute given should be a dictionary.

    Returns:
        A string for the __repr__ method of the class that inherits from pydantic.BaseModel.
    """

    if attr_ignore == None:
        attr_ignore = []
    if attr_multiline == None:
        attr_multiline = []

    def create_wrapped_list(self, attr_ignore=None, attr_multiline=None):
        attribute_list = []
        for field in self.__fields__:
            if field not in attr_ignore:
                value = str(getattr(self, field)).replace("\n", " ").replace("\t", " ")
                if field in attr_multiline:
                    pre_indent = " " * (len(field) - 4)
                    value = f"\n\t{pre_indent}".join(
                        f"'{item[0]}': '{item[1]}'" for item in getattr(self, field).items()
                    )
                attribute_list.append(f"{field}={value}")
        else:
            indent = "   "
            indented_elements = [textwrap.indent(element, prefix=indent) for element in attribute_list]
            return indented_elements

    return_text = ""
    return_text += self.__class__.__name__ + "("
    for attribute in create_wrapped_list(self, attr_ignore=attr_ignore, attr_multiline=attr_multiline):
        return_text += "\n" + attribute
    else:
        return_text += "\n)"

    return return_text
