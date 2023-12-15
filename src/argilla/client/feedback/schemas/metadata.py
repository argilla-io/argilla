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

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, Union

from pydantic import (
    BaseModel,
    Extra,
    Field,
    StrictFloat,
    StrictInt,
    StrictStr,
    ValidationError,
    root_validator,
    validator,
)

from argilla.client.feedback.constants import METADATA_PROPERTY_TYPE_TO_PYDANTIC_TYPE, PYDANTIC_STRICT_TO_PYTHON_TYPE
from argilla.client.feedback.schemas.enums import MetadataPropertyTypes
from argilla.client.feedback.schemas.validators import (
    validate_numeric_metadata_filter_bounds,
    validate_numeric_metadata_property_bounds,
)

TERMS_METADATA_PROPERTY_MIN_VALUES = 1
TERMS_METADATA_FILTER_MIN_VALUES = 1


class MetadataPropertySchema(BaseModel, ABC):
    """Base schema for the `FeedbackDataset` metadata properties.

    Args:
        name: The name of the metadata property.
        title: A title of the metadata property (what's shown in the UI). Defaults to `None`,
            which means that if not provided then the `name` will be used as the `title`.
        visible_for_annotators: Whether the metadata property should be visible for
            users with the `annotator` role. Defaults to `True`.
        type: The type of the metadata property. A value should be set for this
            attribute in the class inheriting from this one to be able to use a
            discriminated union based on the `type` field. Defaults to `None`.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one, as they will have the `type` field already defined, and ensured
        to be supported by Argilla.
    """

    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    title: Optional[str] = None
    visible_for_annotators: Optional[bool] = True
    type: MetadataPropertyTypes = Field(..., allow_mutation=False)

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"type"}

    @validator("title", always=True)
    def title_must_have_value(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        return values.get("name") if not v else v

    @property
    @abstractmethod
    def server_settings(self) -> Dict[str, Any]:
        ...

    def to_server_payload(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "title": self.title,
            "visible_for_annotators": self.visible_for_annotators,
            "settings": self.server_settings,
        }

    @property
    @abstractmethod
    def _pydantic_field_with_validator(self) -> Tuple[Dict[str, Tuple[Any, ...]], Dict[str, Callable]]:
        ...

    @abstractmethod
    def _validate_filter(self, metadata_filter: "MetadataFilters") -> None:
        pass

    def _check_allowed_value_type(self, value: Any) -> Any:
        expected_type = PYDANTIC_STRICT_TO_PYTHON_TYPE[METADATA_PROPERTY_TYPE_TO_PYDANTIC_TYPE[self.type]]
        if not isinstance(value, expected_type):
            raise ValueError(
                f"Provided '{self.name}={value}' of type {type(value)} is not valid, "
                f"only values of type {expected_type} are allowed."
            )
        return value


class TermsMetadataProperty(MetadataPropertySchema):
    """Schema for the `FeedbackDataset` metadata properties of type `terms`. This kind
    of metadata property will be used for filtering the metadata of a record based on
    a list of possible terms or values.

    Args:
        name: The name of the metadata property.
        title: A title of the metadata property (what's shown in the UI). Defaults to `None`,
            which means that if not provided then the `name` will be used as the `title`.
        visible_for_annotators: Whether the metadata property should be visible for
            users with the `annotator` role. Defaults to `True`.
        values: A list of possible values for the metadata property. It must contain
            at least one value.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import TermsMetadataProperty
        >>> TermsMetadataProperty(name="color", values=["red", "blue", "green"])
    """

    type: Literal[MetadataPropertyTypes.terms] = Field(MetadataPropertyTypes.terms.value, allow_mutation=False)
    values: Optional[List[str]] = None

    @validator("values")
    def check_values(cls, terms_values: Union[List[str], None], values: Dict[str, Any]) -> List[str]:
        if terms_values is not None:
            if len(terms_values) < TERMS_METADATA_PROPERTY_MIN_VALUES:
                raise ValueError(
                    f"`TermsMetadataProperty` with name={values.get('name')} must have at least {TERMS_METADATA_PROPERTY_MIN_VALUES} `values`"
                )
            if len(set(terms_values)) != len(terms_values):
                raise ValueError(
                    f"`TermsMetadataProperty` with name={values.get('name')} cannot have repeated `values`"
                )
        return terms_values

    @property
    def server_settings(self) -> Dict[str, Any]:
        settings: Dict[str, Any] = {"type": self.type}
        if self.values is not None:
            settings["values"] = self.values
        return settings

    def _all_values_exist(self, introduced_value: Optional[Union[str, List[str]]] = None) -> Optional[str]:
        if introduced_value is None or self.values is None:
            return introduced_value

        if isinstance(introduced_value, str):
            values = [introduced_value]
        else:
            values = introduced_value

        for value in values:
            if value not in self.values:
                raise ValueError(
                    f"Provided '{self.name}={value}' is not valid, only values in {self.values} are allowed."
                )

        return introduced_value

    def _validator(self, value: Any) -> Any:
        return self._all_values_exist(self._check_allowed_value_type(value))

    @property
    def _pydantic_field_with_validator(self) -> Tuple[Dict[str, Tuple[StrictStr, None]], Dict[str, Callable]]:
        # TODO: Simplify the validation logic and do not base on dynamic pydantic models
        return (
            {self.name: (METADATA_PROPERTY_TYPE_TO_PYDANTIC_TYPE[self.type], None)},
            {f"{self.name}_validator": validator(self.name, allow_reuse=True, pre=True)(self._validator)},
        )

    def _validate_filter(self, metadata_filter: "TermsMetadataFilter") -> None:
        if self.values is not None and not all(value in self.values for value in metadata_filter.values):
            raise ValidationError(
                f"Provided 'values={metadata_filter.values}' is not valid, only values in {self.values} are allowed."
            )


class _NumericMetadataPropertySchema(MetadataPropertySchema):
    """Protected schema for the numeric `FeedbackDataset` metadata properties.

    Args:
        name: The name of the metadata property.
        title: A title of the metadata property (what's shown in the UI). Defaults to `None`,
            which means that if not provided then the `name` will be used as the `title`.
        visible_for_annotators: Whether the metadata property should be visible for
            users with the `annotator` role. Defaults to `True`.
        min: The lower bound of the numeric value. Must be provided and be lower than
            the `max` value.
        max: The upper bound of the numeric value. Must be provided and be greater
            than the `min` value.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one.
    """

    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None

    _bounds_validator = root_validator(allow_reuse=True)(validate_numeric_metadata_property_bounds)

    @property
    def server_settings(self) -> Dict[str, Any]:
        settings: Dict[str, Any] = {"type": self.type}
        if self.min is not None:
            settings["min"] = self.min
        if self.max is not None:
            settings["max"] = self.max
        return settings

    def _value_in_bounds(self, provided_value: Optional[Union[int, float]]) -> Union[int, float]:
        if provided_value is not None:
            if (self.min is not None and self.min > provided_value) or (
                self.max is not None and self.max < provided_value
            ):
                if self.min is not None and self.max is not None:
                    raise ValueError(
                        f"Provided '{self.name}={provided_value}' is not valid, only values between {self.min} and {self.max} are allowed."
                    )
                if self.min is not None:
                    raise ValueError(
                        f"Provided '{self.name}={provided_value}' is not valid, only values over {self.min} are allowed."
                    )
                if self.max is not None:
                    raise ValueError(
                        f"Provided '{self.name}={provided_value}' is not valid, only values under {self.max} are allowed."
                    )
        return provided_value

    def _validator(self, value: Any) -> Any:
        return self._value_in_bounds(self._check_allowed_value_type(value))

    @property
    def _pydantic_field_with_validator(
        self,
    ) -> Tuple[Dict[str, Tuple[Union[StrictInt, StrictFloat], None]], Dict[str, Callable]]:
        return (
            {self.name: (METADATA_PROPERTY_TYPE_TO_PYDANTIC_TYPE[self.type], None)},
            {f"{self.name}_validator": validator(self.name, allow_reuse=True, pre=True)(self._validator)},
        )

    def _validate_filter(self, metadata_filter: Union["IntegerMetadataFilter", "FloatMetadataFilter"]) -> None:
        metadata_filter = metadata_filter.dict()
        for allowed_arg in ["ge", "le"]:
            if metadata_filter[allowed_arg] is not None:
                if (
                    self.max is not None
                    and self.min is not None
                    and not (self.max >= metadata_filter[allowed_arg] >= self.min)
                ):
                    raise ValidationError(
                        f"Provided '{allowed_arg}={metadata_filter[allowed_arg]}' is not valid, only values between {self.min} and {self.max} are allowed."
                    )
                if self.max is not None and not (self.max >= metadata_filter[allowed_arg]):
                    raise ValidationError(
                        f"Provided '{allowed_arg}={metadata_filter[allowed_arg]}' is not valid, only values under {self.max} are allowed."
                    )
                if self.min is not None and not (self.min <= metadata_filter[allowed_arg]):
                    raise ValidationError(
                        f"Provided '{allowed_arg}={metadata_filter[allowed_arg]}' is not valid, only values over {self.min} are allowed."
                    )


class IntegerMetadataProperty(_NumericMetadataPropertySchema):
    """Schema for the `FeedbackDataset` metadata properties of type `integer`. This kind
    of metadata property will be used for filtering the metadata of a record based on
    an integer value to which `min` and `max` filters can be applied.

    Args:
        name: The name of the metadata property.
        title: A title of the metadata property (what's shown in the UI). Defaults to `None`,
            which means that if not provided then the `name` will be used as the `title`.
        visible_for_annotators: Whether the metadata property should be visible for
            users with the `annotator` role. Defaults to `True`.
        min: The lower bound of the integer value. Must be provided, and be lower than
            the `max` value.
        max: The upper bound of the integer value. Must be provided, and be greater than
            the `min` value.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import IntegerMetadataProperty
        >>> IntegerMetadataProperty(name="day", min=0, max=31)
    """

    type: Literal[MetadataPropertyTypes.integer] = Field(MetadataPropertyTypes.integer.value, allow_mutation=False)
    min: Optional[int] = None
    max: Optional[int] = None


class FloatMetadataProperty(_NumericMetadataPropertySchema):
    """Schema for the `FeedbackDataset` metadata properties of type `float`. This kind
    of metadata property will be used for filtering the metadata of a record based on
    an float value to which `min` and `max` filters can be applied.

    Args:
        name: The name of the metadata property.
        title: A title of the metadata property (what's shown in the UI). Defaults to `None`,
            which means that if not provided then the `name` will be used as the `title`.
        visible_for_annotators: Whether the metadata property should be visible for
            users with the `annotator` role. Defaults to `True`.
        min: The lower bound of the float value. Must be provided, and be lower than
            the `max` value.
        max: The upper bound of the float value. Must be provided, and be greater than
            the `min` value.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import FloatMetadataProperty
        >>> FloatMetadataProperty(name="price", min=0.0, max=100.0)
    """

    type: Literal[MetadataPropertyTypes.float] = Field(MetadataPropertyTypes.float.value, allow_mutation=False)
    min: Optional[float] = None
    max: Optional[float] = None


class MetadataFilterSchema(BaseModel, ABC):
    """Base schema for the `FeedbackDataset` metadata filters.

    Args:
        name: The name of the metadata property.
        type: The type of the metadata property. A value should be set for this
            attribute in the class inheriting from this one to be able to use a
            discriminated union based on the `type` field.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one, as they will have the `type` field already defined, and ensured
        to be supported by Argilla.
    """

    name: str = Field(..., regex=r"^(?=.*[a-z0-9])[a-z0-9_-]+$")
    type: MetadataPropertyTypes = Field(..., allow_mutation=False)

    class Config:
        validate_assignment = True
        extra = Extra.forbid
        exclude = {"type"}

    @property
    @abstractmethod
    def query_string(self) -> str:
        ...


class TermsMetadataFilter(MetadataFilterSchema):
    """Schema for the `FeedbackDataset` metadata filters of type `terms`. This kind
    of metadata filter will be used for filtering the metadata of a record based on
    a list of possible terms or values.

    Args:
        name: The name of the metadata property.
        values: A list of possible values for the metadata property. It must contain
            at least two values.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import TermsMetadataFilter
        >>> TermsMetadataFilter(name="color", values=["red", "blue", "green"])
    """

    type: Literal[MetadataPropertyTypes.terms] = Field(MetadataPropertyTypes.terms.value, allow_mutation=False)
    values: List[str] = Field(..., min_items=TERMS_METADATA_FILTER_MIN_VALUES)

    @validator("values")
    def check_values(cls, terms_values: List[str], values: Dict[str, Any]) -> List[str]:
        if len(set(terms_values)) != len(terms_values):
            name = values.get("name")
            raise ValueError(f"`TermsMetadataFilter` with name={name} cannot have repeated `values`")
        return terms_values

    @property
    def query_string(self) -> str:
        return f"{self.name}:{','.join(self.values)}"


class _NumericMetadataFilterSchema(MetadataFilterSchema):
    """Protected schema for the numeric `FeedbackDataset` metadata filters.

    Note:
        At least one of the `le` or `ge` attributes must be provided.

    Args:
        name: The name of the metadata property.
        le: The upper bound of the numeric value. Defaults to `None`.
        ge: The lower bound of the numeric value. Defaults to `None`.

    Disclaimer:
        You should not use this class directly, but instead use the classes that inherit
        from this one.
    """

    le: Optional[Union[int, float]] = None
    ge: Optional[Union[int, float]] = None

    _bounds_validator = root_validator(allow_reuse=True)(validate_numeric_metadata_filter_bounds)

    @property
    def query_string(self) -> str:
        filter_params = {}
        if self.le is not None:
            filter_params["le"] = self.le
        if self.ge is not None:
            filter_params["ge"] = self.ge
        return f"{self.name}:{filter_params}".replace("'", '"')


class IntegerMetadataFilter(_NumericMetadataFilterSchema):
    """Schema for the `FeedbackDataset` metadata filters of type `integer`. This kind
    of metadata filter will be used for filtering the metadata of a record based on
    an integer value to which `le` and `ge` filters can be applied.

    Note:
        At least one of the `le` or `ge` attributes must be provided.

    Args:
        name: The name of the metadata property.
        le: The upper bound of the integer value. Defaults to `None`.
        ge: The lower bound of the integer value. Defaults to `None`.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import IntegerMetadataFilter
        >>> IntegerMetadataFilter(name="day", le=15)
        >>> IntegerMetadataFilter(name="day", ge=15)
        >>> IntegerMetadataFilter(name="day", le=15, ge=10)
    """

    type: Literal[MetadataPropertyTypes.integer] = Field(MetadataPropertyTypes.integer.value, allow_mutation=False)
    le: Optional[int] = None
    ge: Optional[int] = None


class FloatMetadataFilter(_NumericMetadataFilterSchema):
    """Schema for the `FeedbackDataset` metadata filters of type `float`. This kind
    of metadata filter will be used for filtering the metadata of a record based on
    an float value to which `le` and `ge` filters can be applied.

    Note:
        At least one of the `le` or `ge` attributes must be provided.

    Args:
        name: The name of the metadata property.
        le: The upper bound of the float value. Defaults to `None`.
        ge: The lower bound of the float value. Defaults to `None`.

    Examples:
        >>> from argilla.client.feedback.schemas.metadata import FloatMetadataFilter
        >>> FloatMetadataFilter(name="price", le=15.0)
        >>> FloatMetadataFilter(name="price", ge=15.0)
        >>> FloatMetadataFilter(name="price", le=15.0, ge=10.0)
    """

    type: Literal[MetadataPropertyTypes.float] = Field(MetadataPropertyTypes.float.value, allow_mutation=False)
    le: Optional[float] = None
    ge: Optional[float] = None


MetadataFilters = Union[TermsMetadataFilter, IntegerMetadataFilter, FloatMetadataFilter]
