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

from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Iterable
from uuid import UUID, uuid4

from argilla._models import (
    MetadataModel,
    RecordModel,
    UserResponseModel,
    SuggestionModel,
    VectorModel,
    MetadataValue,
)
from argilla._resource import Resource
from argilla.responses import Response, UserResponse
from argilla.suggestions import Suggestion
from argilla.vectors import Vector

if TYPE_CHECKING:
    from argilla.datasets import Dataset


class Record(Resource):
    """The class for interacting with Argilla Records. A `Record` is a single sample
    in a dataset. Records receives feedback in the form of responses and suggestions.
    Records contain fields, metadata, and vectors.

    Attributes:
        id (Union[str, UUID]): The id of the record.
        fields (RecordFields): The fields of the record.
        metadata (RecordMetadata): The metadata of the record.
        vectors (RecordVectors): The vectors of the record.
        responses (RecordResponses): The responses of the record.
        suggestions (RecordSuggestions): The suggestions of the record.
        dataset (Dataset): The dataset to which the record belongs.
        _server_id (UUID): An id for the record generated by the Argilla server.
    """

    _model: RecordModel

    def __init__(
        self,
        id: Optional[Union[UUID, str]] = None,
        fields: Optional[Dict[str, Union[str, None]]] = None,
        metadata: Optional[Dict[str, MetadataValue]] = None,
        vectors: Optional[List[Vector]] = None,
        responses: Optional[List[Response]] = None,
        suggestions: Optional[List[Suggestion]] = None,
        _server_id: Optional[UUID] = None,
        _dataset: Optional["Dataset"] = None,
    ):
        """Initializes a Record with fields, metadata, vectors, responses, suggestions, external_id, and id.
        Records are typically defined as flat dictionary objects with fields, metadata, vectors, responses, and suggestions
        and passed to Dataset.DatasetRecords.add() as a list of dictionaries.

        Args:
            id: An id for the record. If not provided, a UUID will be generated.
            fields: A dictionary of fields for the record.
            metadata: A dictionary of metadata for the record.
            vectors: A dictionary of vectors for the record.
            responses: A list of Response objects for the record.
            suggestions: A list of Suggestion objects for the record.
            _server_id: An id for the record. (Read-only and set by the server)
            _dataset: The dataset object to which the record belongs.
        """
        if fields is None and metadata is None and vectors is None and responses is None and suggestions is None:
            raise ValueError("At least one of fields, metadata, vectors, responses, or suggestions must be provided.")
        if fields is None and id is None:
            raise ValueError("If fields are not provided, an id must be provided.")
        if fields == {} and id is None:
            raise ValueError("If fields are an empty dictionary, an id must be provided.")
        self._dataset = _dataset

        self._model = RecordModel(
            fields=fields,
            external_id=id or uuid4(),
            id=_server_id,
        )
        # TODO: All this code blocks could be define as property setters
        # Initialize the fields
        self.__fields = RecordFields(fields=self._model.fields)
        # Initialize the vectors
        self.__vectors = RecordVectors(vectors=vectors, record=self)
        # Initialize the metadata
        self.__metadata = RecordMetadata(metadata=metadata)
        self.__responses = RecordResponses(responses=responses, record=self)
        self.__suggestions = RecordSuggestions(suggestions=suggestions, record=self)

    def __repr__(self) -> str:
        return (
            f"Record(id={self.id},fields={self.fields},metadata={self.metadata},"
            f"suggestions={self.suggestions},responses={self.responses})"
        )

    ############################
    # Properties
    ############################

    @property
    def id(self) -> str:
        return self._model.external_id

    @id.setter
    def id(self, value: str) -> None:
        self._model.external_id = value

    @property
    def dataset(self) -> "Dataset":
        return self._dataset

    @dataset.setter
    def dataset(self, value: "Dataset") -> None:
        self._dataset = value

    @property
    def fields(self) -> "RecordFields":
        return self.__fields

    @property
    def responses(self) -> "RecordResponses":
        return self.__responses

    @property
    def suggestions(self) -> "RecordSuggestions":
        return self.__suggestions

    @property
    def metadata(self) -> "RecordMetadata":
        return self.__metadata

    @property
    def vectors(self) -> "RecordVectors":
        return self.__vectors

    @property
    def _server_id(self) -> Optional[UUID]:
        return self._model.id

    ############################
    # Public methods
    ############################

    def api_model(self) -> RecordModel:
        return RecordModel(
            id=self._model.id,
            external_id=self._model.external_id,
            fields=self.fields.to_dict(),
            metadata=self.metadata.api_models(),
            vectors=self.vectors.models,
            responses=self.responses.api_models(),
            suggestions=self.suggestions.api_models(),
        )

    def serialize(self) -> Dict[str, Any]:
        """Serializes the Record to a dictionary for interaction with the API"""
        serialized_model = self._model.model_dump()
        serialized_suggestions = [suggestion.serialize() for suggestion in self.__suggestions]
        serialized_responses = [response.serialize() for response in self.__responses]
        serialized_model["responses"] = serialized_responses
        serialized_model["suggestions"] = serialized_suggestions
        return serialized_model

    def to_dict(self) -> Dict[str, Dict]:
        """Converts a Record object to a dictionary for export.
        Returns:
            A dictionary representing the record where the keys are "fields",
            "metadata", "suggestions", and "responses". Each field and question is
            represented as a key-value pair in the dictionary of the respective key. i.e.
            `{"fields": {"prompt": "...", "response": "..."}, "responses": {"rating": "..."},
        """
        fields = self.fields.to_dict()
        metadata = dict(self.metadata)
        suggestions = self.suggestions.to_dict()
        responses = self.responses.to_dict()
        vectors = self.vectors.to_dict()
        return {
            "id": self.id,
            "fields": fields,
            "metadata": metadata,
            "suggestions": suggestions,
            "responses": responses,
            "vectors": vectors,
            "_server_id": str(self._model.id) if self._model.id else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Dict], dataset: Optional["Dataset"] = None) -> "Record":
        """Converts a dictionary to a Record object.
        Args:
            data: A dictionary representing the record.
            dataset: The dataset object to which the record belongs.
        Returns:
            A Record object.
        """
        fields = data.get("fields", {})
        metadata = data.get("metadata", {})
        suggestions = data.get("suggestions", {})
        responses = data.get("responses", {})
        vectors = data.get("vectors", {})
        record_id = data.get("id", None)
        _server_id = data.get("_server_id", None)

        suggestions = [Suggestion(question_name=question_name, **value) for question_name, value in suggestions.items()]
        responses = [
            Response(question_name=question_name, **value)
            for question_name, _responses in responses.items()
            for value in _responses
        ]
        vectors = [Vector(name=vector_name, values=values) for vector_name, values in vectors.items()]

        return cls(
            id=record_id,
            fields=fields,
            suggestions=suggestions,
            responses=responses,
            vectors=vectors,
            metadata=metadata,
            _dataset=dataset,
            _server_id=_server_id,
        )

    @classmethod
    def from_model(cls, model: RecordModel, dataset: "Dataset") -> "Record":
        """Converts a RecordModel object to a Record object.
        Args:
            model: A RecordModel object.
            dataset: The dataset object to which the record belongs.
        Returns:
            A Record object.
        """
        return cls(
            id=model.external_id,
            fields=model.fields,
            metadata={meta.name: meta.value for meta in model.metadata},
            vectors=[Vector.from_model(model=vector) for vector in model.vectors],
            # Responses and their models are not aligned 1-1.
            responses=[
                response
                for response_model in model.responses
                for response in UserResponse.from_model(response_model, dataset=dataset)
            ],
            suggestions=[Suggestion.from_model(model=suggestion, dataset=dataset) for suggestion in model.suggestions],
            _dataset=dataset,
            _server_id=model.id,
        )


class RecordFields:
    """This is a container class for the fields of a Record.
    It allows for accessing fields by attribute and iterating over them.
    """

    def __init__(self, fields: Dict[str, Union[str, None]]) -> None:
        self.__fields = fields or {}
        for key, value in self.__fields.items():
            setattr(self, key, value)

    def __getitem__(self, key: str) -> Optional[str]:
        return self.__fields.get(key)

    def __iter__(self):
        return iter(self.__fields)

    def to_dict(self) -> Dict[str, Union[str, None]]:
        return self.__fields

    def __repr__(self) -> str:
        return self.to_dict().__repr__()

class RecordMetadata(dict):
    """This is a container class for the metadata of a Record."""

    def __init__(self, metadata: Optional[Dict[str, MetadataValue]] = None) -> None:
        super().__init__(metadata or {})

    def __getattr__(self, item: str):
        return self[item]

    def __setattr__(self, key: str, value: MetadataValue):
        self[key] = value

    def api_models(self) -> List[MetadataModel]:
        return [MetadataModel(name=key, value=value) for key, value in self.items()]


class RecordResponses(Iterable[Response]):
    """This is a container class for the responses of a Record.
    It allows for accessing responses by attribute and iterating over them.
    A record can have multiple responses per question so we set the response
    in a list default dictionary with the question name as the key.
    """

    def __init__(self, responses: List[Response], record: Record) -> None:
        self.record = record
        self.__responses_by_question_name = defaultdict(list)

        self.__responses = responses or []
        for response in self.__responses:
            response.record = self.record
            self.__responses_by_question_name[response.question_name].append(response)

    def __iter__(self):
        return iter(self.__responses)

    def __getitem__(self, index: int):
        return self.__responses[index]

    def __getattr__(self, name) -> List[Response]:
        return self.__responses_by_question_name[name]

    def __repr__(self) -> str:
        return {k: [{"value": v["value"]} for v in values] for k, values in self.to_dict().items()}.__repr__()

    def api_models(self) -> List[UserResponseModel]:
        """Returns a list of ResponseModel objects."""

        responses_by_user_id = defaultdict(list)
        for response in self.__responses:
            responses_by_user_id[response.user_id].append(response)

        return [
            UserResponse(answers=responses, _record=self.record).api_model()
            for responses in responses_by_user_id.values()
        ]

    def to_dict(self) -> Dict[str, List[Dict]]:
        """Converts the responses to a dictionary.
        Returns:
            A dictionary of responses.
        """
        response_dict = defaultdict(list)
        for response in self.__responses:
            response_dict[response.question_name].append({"value": response.value, "user_id": response.user_id})
        return response_dict


class RecordSuggestions(Iterable[Suggestion]):
    """This is a container class for the suggestions of a Record.
    It allows for accessing suggestions by attribute and iterating over them.
    """

    def __init__(self, suggestions: List[Suggestion], record: Record) -> None:
        self.record = record

        self.__suggestions = suggestions or []
        for suggestion in self.__suggestions:
            suggestion.record = self.record
            setattr(self, suggestion.question_name, suggestion)

    def api_models(self) -> List[SuggestionModel]:
        return [suggestion.api_model() for suggestion in self.__suggestions]

    def __iter__(self):
        return iter(self.__suggestions)

    def __getitem__(self, index: int):
        return self.__suggestions[index]

    def to_dict(self) -> Dict[str, List[str]]:
        """Converts the suggestions to a dictionary.
        Returns:
            A dictionary of suggestions.
        """
        suggestion_dict: dict = {}
        for suggestion in self.__suggestions:
            suggestion_dict[suggestion.question_name] = {
                "value": suggestion.value,
                "score": suggestion.score,
                "agent": suggestion.agent,
            }
        return suggestion_dict

    def __repr__(self) -> str:
        return self.to_dict().__repr__()


class RecordVectors:
    """This is a container class for the vectors of a Record.
    It allows for accessing suggestions by attribute and iterating over them.
    """

    def __init__(self, vectors: List[Vector], record: Record) -> None:
        self.__vectors = vectors or []
        self.record = record
        for vector in self.__vectors:
            setattr(self, vector.name, vector.values)

    def __repr__(self) -> str:
        return {vector.name: f"{len(vector.values)}" for vector in self.__vectors}.__repr__()

    @property
    def models(self) -> List[VectorModel]:
        return [vector.api_model() for vector in self.__vectors]

    def to_dict(self) -> Dict[str, List[float]]:
        """Converts the vectors to a dictionary.
        Returns:
            A dictionary of vectors.
        """
        return {vector.name: list(map(float, vector.values)) for vector in self.__vectors}

