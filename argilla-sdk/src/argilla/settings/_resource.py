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

import json
import os
from functools import cached_property
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Dict, Union, Iterator, Sequence
from uuid import UUID

from argilla._exceptions import SettingsError, ArgillaAPIError, ArgillaSerializeError
from argilla._models._dataset import DatasetModel
from argilla._resource import Resource
from argilla.settings._field import TextField
from argilla.settings._metadata import MetadataType, MetadataField
from argilla.settings._question import QuestionType, question_from_model, question_from_dict, QuestionPropertyBase
from argilla.settings._vector import VectorField

if TYPE_CHECKING:
    from argilla.datasets import Dataset


__all__ = ["Settings"]


class Settings(Resource):
    """
    Settings class for Argilla Datasets.

    This class is used to define the representation of a Dataset within the UI.
    """

    def __init__(
        self,
        fields: Optional[List[TextField]] = None,
        questions: Optional[List[QuestionType]] = None,
        vectors: Optional[List[VectorField]] = None,
        metadata: Optional[List[MetadataType]] = None,
        guidelines: Optional[str] = None,
        allow_extra_metadata: bool = False,
        _dataset: Optional["Dataset"] = None,
    ) -> None:
        """
        Args:
            fields (List[TextField]): A list of TextField objects that represent the fields in the Dataset.
            questions (List[Union[LabelQuestion, MultiLabelQuestion, RankingQuestion, TextQuestion, RatingQuestion]]): A list of Question objects that represent the questions in the Dataset.
            vectors (List[VectorField]): A list of VectorField objects that represent the vectors in the Dataset.
            metadata (List[MetadataField]): A list of MetadataField objects that represent the metadata in the Dataset.
            guidelines (str): A string containing the guidelines for the Dataset.
            allow_extra_metadata (bool): A boolean that determines whether or not extra metadata is allowed in the Dataset. Defaults to False.
        """
        super().__init__(client=_dataset._client if _dataset else None)

        self.__questions = questions or []
        self.__fields = SettingsProperties(self, fields)
        self.__vectors = SettingsProperties(self, vectors)
        self.__metadata = SettingsProperties(self, metadata)

        self.__guidelines = self.__process_guidelines(guidelines)
        self.__allow_extra_metadata = allow_extra_metadata

        self._dataset = _dataset

    #####################
    # Properties        #
    #####################

    @property
    def fields(self) -> "SettingsProperties":
        return self.__fields

    @fields.setter
    def fields(self, fields: List[TextField]):
        self.__fields = SettingsProperties(self, fields)

    @property
    def questions(self) -> List[QuestionType]:
        return self.__questions

    @questions.setter
    def questions(self, questions: List[QuestionType]):
        self.__questions = questions

    @property
    def vectors(self) -> "SettingsProperties":
        return self.__vectors

    @vectors.setter
    def vectors(self, vectors: List[VectorField]):
        self.__vectors = SettingsProperties(self, vectors)

    @property
    def metadata(self) -> "SettingsProperties":
        return self.__metadata

    @metadata.setter
    def metadata(self, metadata: List[MetadataType]):
        self.__metadata = SettingsProperties(self, metadata)

    @property
    def guidelines(self) -> str:
        return self.__guidelines

    @guidelines.setter
    def guidelines(self, guidelines: str):
        self.__guidelines = self.__process_guidelines(guidelines)

    @property
    def allow_extra_metadata(self) -> bool:
        return self.__allow_extra_metadata

    @allow_extra_metadata.setter
    def allow_extra_metadata(self, value: bool):
        self.__allow_extra_metadata = value

    @property
    def dataset(self) -> "Dataset":
        return self._dataset

    @dataset.setter
    def dataset(self, dataset: "Dataset"):
        self._dataset = dataset
        self._client = dataset._client

    @cached_property
    def schema(self) -> dict:
        schema_dict = {}

        for field in self.fields:
            schema_dict[field.name] = field

        for question in self.questions:
            schema_dict[question.name] = question

        for vector in self.vectors:
            schema_dict[vector.name] = vector

        for metadata in self.metadata:
            schema_dict[metadata.name] = metadata

        return schema_dict

    @cached_property
    def schema_by_id(self) -> Dict[UUID, Union[TextField, QuestionType, MetadataType, VectorField]]:
        return {v.id: v for v in self.schema.values()}

    def validate(self) -> None:
        self._validate_empty_settings()
        self._validate_duplicate_names()

    #####################
    #  Public methods   #
    #####################

    def get(self) -> "Settings":
        self.fields = self._fetch_fields()
        self.questions = self._fetch_questions()
        self.vectors = self._fetch_vectors()
        self.metadata = self._fetch_metadata()
        self.__get_dataset_related_attributes()

        self._update_last_api_call()
        return self

    def create(self) -> "Settings":
        self.validate()

        self._update_dataset_related_attributes()
        self.__fields.create()
        self._create_questions()
        self.__vectors.create()
        self.__metadata.create()

        self._update_last_api_call()
        return self

    def update(self) -> "Resource":
        self.validate()

        self._update_dataset_related_attributes()
        self.__fields.update()
        self.__vectors.update()
        self.__metadata.update()
        # self.questions.update()

        self._update_last_api_call()
        return self

    def question_by_name(self, question_name: str) -> QuestionType:
        for question in self.questions:
            if question.name == question_name:
                return question
        raise ValueError(f"Question with name {question_name} not found")

    def question_by_id(self, question_id: UUID) -> QuestionType:
        property = self.schema_by_id.get(question_id)
        if isinstance(property, QuestionPropertyBase):
            return property
        raise ValueError(f"Question with id {question_id} not found")

    def serialize(self):
        try:
            return {
                "guidelines": self.guidelines,
                "questions": self.__serialize_questions(self.questions),
                "fields": self.__fields.serialize(),
                "vectors": self.vectors.serialize(),
                "metadata": self.metadata.serialize(),
                "allow_extra_metadata": self.allow_extra_metadata,
            }
        except Exception as e:
            raise ArgillaSerializeError(f"Failed to serialize the settings. {e.__class__.__name__}") from e

    def to_json(self, path: Union[Path, str]) -> None:
        """Save the settings to a file on disk

        Parameters:
            path (str): The path to save the settings to
        """
        if not isinstance(path, Path):
            path = Path(path)
        if path.exists():
            raise FileExistsError(f"File {path} already exists")
        with open(path, "w") as file:
            json.dump(self.serialize(), file)

    @classmethod
    def from_json(cls, path: Union[Path, str]) -> "Settings":
        """Load the settings from a file on disk"""

        with open(path, "r") as file:
            settings_dict = json.load(file)

        fields = settings_dict.get("fields", [])
        vectors = settings_dict.get("vectors", [])
        metadata = settings_dict.get("metadata", [])
        guidelines = settings_dict.get("guidelines")
        allow_extra_metadata = settings_dict.get("allow_extra_metadata")

        questions = [question_from_dict(question) for question in settings_dict.get("questions", [])]
        fields = [TextField.from_dict(field) for field in fields]
        vectors = [VectorField.from_dict(vector) for vector in vectors]
        metadata = [MetadataField.from_dict(metadata) for metadata in metadata]

        return cls(
            questions=questions,
            fields=fields,
            vectors=vectors,
            metadata=metadata,
            guidelines=guidelines,
            allow_extra_metadata=allow_extra_metadata,
        )

    def __eq__(self, other: "Settings") -> bool:
        return self.serialize() == other.serialize()  # TODO: Create proper __eq__ methods for fields and questions

    #####################
    #  Repr Methods     #
    #####################

    def __repr__(self) -> str:
        return (
            f"Settings(guidelines={self.guidelines}, allow_extra_metadata={self.allow_extra_metadata}, "
            f"fields={self.fields}, questions={self.questions}, vectors={self.vectors}, metadata={self.metadata})"
        )

    #####################
    #  Private methods  #
    #####################

    def _fetch_fields(self) -> List[TextField]:
        models = self._client.api.fields.list(dataset_id=self._dataset.id)
        return [TextField.from_model(model) for model in models]

    def _fetch_questions(self) -> List[QuestionType]:
        models = self._client.api.questions.list(dataset_id=self._dataset.id)
        return [question_from_model(model) for model in models]

    def _fetch_vectors(self) -> List[VectorField]:
        models = self.dataset._client.api.vectors.list(self.dataset.id)
        return [VectorField.from_model(model) for model in models]

    def _fetch_metadata(self) -> List[MetadataType]:
        models = self._client.api.metadata.list(dataset_id=self._dataset.id)
        return [MetadataField.from_model(model) for model in models]

    def __get_dataset_related_attributes(self):
        # This flow may be a bit weird, but it's the only way to update the dataset related attributes
        # Everything is point that we should have several settings-related endpoints in the API to handle this.
        # POST /api/v1/datasets/{dataset_id}/settings
        # {
        #   "guidelines": ....,
        #   "allow_extra_metadata": ....,
        # }
        # But this is not implemented yet, so we need to update the dataset model directly
        dataset_model = self._client.api.datasets.get(self._dataset.id)

        self.guidelines = dataset_model.guidelines
        self.allow_extra_metadata = dataset_model.allow_extra_metadata

    def _update_dataset_related_attributes(self):
        # This flow may be a bit weird, but it's the only way to update the dataset related attributes
        # Everything is point that we should have several settings-related endpoints in the API to handle this.
        # POST /api/v1/datasets/{dataset_id}/settings
        # {
        #   "guidelines": ....,
        #   "allow_extra_metadata": ....,
        # }
        # But this is not implemented yet, so we need to update the dataset model directly
        dataset_model = DatasetModel(
            id=self._dataset.id,
            name=self._dataset.name,
            guidelines=self.guidelines,
            allow_extra_metadata=self.allow_extra_metadata,
        )
        self._client.api.datasets.update(dataset_model)

    def _create_questions(self) -> None:
        for question in self.__questions:
            try:
                question_model = self._client.api.questions.create(
                    dataset_id=self._dataset.id, question=question._model
                )
                question._model = question_model
            except ArgillaAPIError as e:
                raise SettingsError(f"Failed to create question {question.name}") from e

    def _validate_empty_settings(self):
        if not all([self.fields, self.questions]):
            message = "Fields and questions are required"
            raise SettingsError(message=message)

    def _validate_duplicate_names(self) -> None:
        dataset_properties_by_name = {}

        for properties in [self.fields, self.questions, self.vectors, self.metadata]:
            for property in properties:
                if property.name in dataset_properties_by_name:
                    raise SettingsError(
                        f"names of dataset settings must be unique, "
                        f"but the name {property.name!r} is used by {type(property).__name__!r} and {type(dataset_properties_by_name[property.name]).__name__!r} "
                    )
                dataset_properties_by_name[property.name] = property

    def __process_guidelines(self, guidelines):
        if guidelines is None:
            return guidelines

        if not isinstance(guidelines, str):
            raise SettingsError("Guidelines must be a string or a path to a file")

        if os.path.exists(guidelines):
            with open(guidelines, "r") as file:
                return file.read()

        return guidelines

    def __serialize_questions(self, questions: List[QuestionType]):
        return [question.serialize() for question in questions]


Property = Union[TextField, VectorField, MetadataType, QuestionType]


class SettingsProperties(Sequence[Property]):
    """A collection of properties (fields, questions, vectors and metadata) for a dataset settings object.

    This class is used to store the properties of a dataset settings object
    """

    def __init__(self, settings: "Settings", properties: List[Property]):
        self._properties_by_name = {}
        self._settings = settings

        for property in properties or []:
            self.add(property)

    def __getitem__(self, key: Union[str, int]) -> Optional[Property]:
        if isinstance(key, int):
            return list(self._properties_by_name.values())[key]
        return self._properties_by_name.get(key)

    def __iter__(self) -> Iterator[Property]:
        return iter(self._properties_by_name.values())

    def __len__(self):
        return len(self._properties_by_name)

    def __eq__(self, other):
        """Check if two instances are equal. Overloads the == operator."""
        if not isinstance(other, SettingsProperties):
            return False
        return self._properties_by_name == other._properties_by_name

    def add(self, property: Property) -> Property:
        self._validate_new_property(property)
        self._properties_by_name[property.name] = property
        setattr(self, property.name, property)
        return property

    def create(self):
        for property in self:
            try:
                property.dataset = self._settings.dataset
                property.create()
            except ArgillaAPIError as e:
                raise SettingsError(f"Failed to create property {property.name!r}: {e.message}") from e

    def update(self):
        for item in self:
            try:
                item.dataset = self._settings.dataset
                item.update() if item.id else item.create()
            except ArgillaAPIError as e:
                raise SettingsError(f"Failed to update {item.name!r}: {e.message}") from e

    def serialize(self) -> List[dict]:
        return [property.serialize() for property in self]

    def _validate_new_property(self, property: Property) -> None:
        if property.name in self._properties_by_name:
            raise ValueError(f"Property with name {property.name!r} already exists in the collection")

        if property.name in dir(self):
            raise ValueError(f"Property with name {property.name!r} conflicts with an existing attribute")
