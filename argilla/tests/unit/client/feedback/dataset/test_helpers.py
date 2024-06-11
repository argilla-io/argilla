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

from typing import TYPE_CHECKING, Dict, List, Type, Union

import pytest
from argilla_v1.client.feedback.dataset.helpers import generate_pydantic_schema_for_metadata
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.remote.metadata import (
    RemoteFloatMetadataProperty,
    RemoteIntegerMetadataProperty,
    RemoteTermsMetadataProperty,
)

from tests.pydantic_v1 import ValidationError

if TYPE_CHECKING:
    from argilla_v1.client.feedback.schemas.types import (
        AllowedMetadataPropertyTypes,
        AllowedRemoteMetadataPropertyTypes,
    )


@pytest.mark.parametrize(
    "metadata_properties, validation_data",
    [
        (
            [TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
            {"terms-metadata": "a"},
        ),
        (
            [IntegerMetadataProperty(name="int-metadata", min=0, max=10)],
            {"int-metadata": 1},
        ),
        (
            [FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            {"float-metadata": 1.0},
        ),
        (
            [
                TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
                IntegerMetadataProperty(name="int-metadata", min=0, max=10),
                FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
            ],
            {"terms-metadata": "a", "int-metadata": 1, "float-metadata": 1.0},
        ),
    ],
)
def test_generate_pydantic_schema_for_metadata(
    metadata_properties: List["AllowedMetadataPropertyTypes"], validation_data: Dict[str, Union[str, int, float]]
) -> None:
    MetadataSchema = generate_pydantic_schema_for_metadata(
        metadata_properties=metadata_properties, name="MetadataSchema"
    )
    assert MetadataSchema(**validation_data)


@pytest.mark.parametrize(
    "metadata_properties, validation_data, exception_cls, exception_msg",
    [
        (
            [TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
            {"terms-metadata": "d"},
            ValidationError,
            "terms-metadata\n  Provided 'terms-metadata=d' is not valid, only values in \['a', 'b', 'c'\] are allowed",
        ),
        (
            [TermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
            {"terms-metadata": 1},
            ValidationError,
            "Provided 'terms-metadata=1' of type <class 'int'> is not valid",
        ),
        (
            [IntegerMetadataProperty(name="int-metadata", min=0, max=10)],
            {"int-metadata": -10},
            ValidationError,
            "int-metadata\n  Provided 'int-metadata=-10' is not valid, only values between 0 and 10 are allowed.",
        ),
        (
            [IntegerMetadataProperty(name="int-metadata", min=0, max=10)],
            {"int-metadata": "wrong"},
            ValidationError,
            "Provided 'int-metadata=wrong' of type <class 'str'> is not valid",
        ),
        (
            [IntegerMetadataProperty(name="int-metadata", min=0, max=10)],
            {"int-metadata": float("nan")},
            ValidationError,
            "Provided 'int-metadata=nan' is not valid, NaN values are not allowed.",
        ),
        (
            [FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            {"float-metadata": 100.0},
            ValidationError,
            "float-metadata\n  Provided 'float-metadata=100.0' is not valid, only values between 0.0 and 10.0 are allowed.",
        ),
        (
            [FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            {"float-metadata": "wrong"},
            ValidationError,
            "Provided 'float-metadata=wrong' of type <class 'str'> is not valid",
        ),
        (
            [FloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            {"float-metadata": float("nan")},
            ValidationError,
            "Provided 'float-metadata=nan' is not valid, NaN values are not allowed.",
        ),
    ],
)
def test_generate_pydantic_schema_for_metadata_errors(
    metadata_properties: List["AllowedMetadataPropertyTypes"],
    validation_data: Dict[str, Union[str, int, float]],
    exception_cls: Exception,
    exception_msg: str,
) -> None:
    MetadataSchema = generate_pydantic_schema_for_metadata(
        metadata_properties=metadata_properties, name="MetadataSchema"
    )
    with pytest.raises(exception_cls, match=exception_msg):
        MetadataSchema(**validation_data)


@pytest.mark.parametrize(
    "metadata_properties, validation_data",
    [
        (
            [RemoteTermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
            {"terms-metadata": "a"},
        ),
        (
            [RemoteIntegerMetadataProperty(name="int-metadata", min=0, max=10)],
            {"int-metadata": 1},
        ),
        (
            [RemoteFloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            {"float-metadata": 1.0},
        ),
        (
            [
                RemoteTermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"]),
                RemoteIntegerMetadataProperty(name="int-metadata", min=0, max=10),
                RemoteFloatMetadataProperty(name="float-metadata", min=0.0, max=10.0),
            ],
            {"terms-metadata": "a", "int-metadata": 1, "float-metadata": 1.0},
        ),
    ],
)
def test_generate_pydantic_schema_for_remote_metadata(
    metadata_properties: List["AllowedRemoteMetadataPropertyTypes"], validation_data: Dict[str, Union[str, int, float]]
) -> None:
    RemoteMetadataSchema = generate_pydantic_schema_for_metadata(
        metadata_properties=metadata_properties, name="RemoteMetadataSchema"
    )
    assert RemoteMetadataSchema(**validation_data).dict() == validation_data


@pytest.mark.parametrize(
    "metadata_properties, validation_data, exception_cls, exception_msg",
    [
        (
            [RemoteTermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
            {"terms-metadata": "d"},
            ValidationError,
            "terms-metadata\n  Provided 'terms-metadata=d' is not valid, only values in \['a', 'b', 'c'\] are allowed",
        ),
        (
            [RemoteTermsMetadataProperty(name="terms-metadata", values=["a", "b", "c"])],
            {"terms-metadata": 1},
            ValidationError,
            "Provided 'terms-metadata=1' of type <class 'int'> is not valid",
        ),
        (
            [RemoteIntegerMetadataProperty(name="int-metadata", min=0, max=10)],
            {"int-metadata": -10},
            ValidationError,
            "int-metadata\n  Provided 'int-metadata=-10' is not valid, only values between 0 and 10 are allowed.",
        ),
        (
            [RemoteIntegerMetadataProperty(name="int-metadata", min=0, max=10)],
            {"int-metadata": "wrong"},
            ValidationError,
            "Provided 'int-metadata=wrong' of type <class 'str'> is not valid",
        ),
        (
            [RemoteFloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            {"float-metadata": 100.0},
            ValidationError,
            "float-metadata\n  Provided 'float-metadata=100.0' is not valid, only values between 0.0 and 10.0 are allowed.",
        ),
        (
            [RemoteFloatMetadataProperty(name="float-metadata", min=0.0, max=10.0)],
            {"float-metadata": "wrong"},
            ValidationError,
            "Provided 'float-metadata=wrong' of type <class 'str'> is not valid",
        ),
    ],
)
def test_generate_pydantic_schema_for_remote_metadata_errors(
    metadata_properties: List["AllowedRemoteMetadataPropertyTypes"],
    validation_data: Dict[str, Union[str, int, float]],
    exception_cls: Type[Exception],
    exception_msg: str,
) -> None:
    RemoteMetadataSchema = generate_pydantic_schema_for_metadata(
        metadata_properties=metadata_properties, name="RemoteMetadataSchema"
    )
    with pytest.raises(exception_cls, match=exception_msg):
        RemoteMetadataSchema(**validation_data)
