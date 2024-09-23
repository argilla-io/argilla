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
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Union
from uuid import UUID

from argilla._exceptions import ArgillaError
from argilla._helpers._media import cast_image, uncast_image
from argilla._models import (
    FieldValue,
    MetadataModel,
    MetadataValue,
    RecordModel,
    SuggestionModel,
    UserResponseModel,
    VectorModel,
    VectorValue,
)
from argilla._resource import Resource
from argilla.responses import Response, UserResponse
from argilla.suggestions import Suggestion
from argilla.vectors import Vector

if TYPE_CHECKING:
    from argilla.datasets import Dataset
    from argilla import Argilla
    from argilla._api import RecordsAPI


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
        fields: Optional[Dict[str, FieldValue]] = None,
        metadata: Optional[Dict[str, MetadataValue]] = None,
        vectors: Optional[Dict[str, VectorValue]] = None,
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
        self._model = RecordModel(external_id=id, id=_server_id)
        self.__fields = RecordFields(fields=fields, record=self)
        self.__vectors = RecordVectors(vectors=vectors)
        self.__metadata = RecordMetadata(metadata=metadata)
        self.__responses = RecordResponses(responses=responses, record=self)
        self.__suggestions = RecordSuggestions(suggestions=suggestions, record=self)

    def __repr__(self) -> str:
        return (
            f"Record(id={self.id},status={self.status},fields={self.fields},metadata={self.metadata},"
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
    def status(self) -> str:
        return self._model.status

    @property
    def _server_id(self) -> Optional[UUID]:
        return self._model.id

    ############################
    # Public methods
    ############################

    def get(self) -> "Record":
        """Retrieves the record from the server."""
        model = self._client.api.records.get(self._server_id)
        instance = self.from_model(model, dataset=self.dataset)
        self.__dict__ = instance.__dict__

        return self

    def api_model(self) -> RecordModel:
        return RecordModel(
            id=self._model.id,
            external_id=self._model.external_id,
            fields=self.fields.to_dict(),
            metadata=self.metadata.api_models(),
            vectors=self.vectors.api_models(),
            responses=self.responses.api_models(),
            suggestions=self.suggestions.api_models(),
            status=self.status,
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
        id = str(self.id) if self.id else None
        server_id = str(self._model.id) if self._model.id else None
        status = self.status
        fields = self.fields.to_dict()
        metadata = self.metadata.to_dict()
        suggestions = self.suggestions.to_dict()
        responses = self.responses.to_dict()
        vectors = self.vectors.to_dict()

        return {
            "id": id,
            "fields": fields,
            "metadata": metadata,
            "suggestions": suggestions,
            "responses": responses,
            "vectors": vectors,
            "status": status,
            "_server_id": server_id,
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
        instance = cls(
            id=model.external_id,
            fields=model.fields,
            metadata={meta.name: meta.value for meta in model.metadata},
            vectors={vector.name: vector.vector_values for vector in model.vectors},
            # Responses and their models are not aligned 1-1.
            responses=[
                response
                for response_model in model.responses
                for response in UserResponse.from_model(response_model, dataset=dataset)
            ],
            suggestions=[Suggestion.from_model(model=suggestion, dataset=dataset) for suggestion in model.suggestions],
        )

        # set private attributes
        instance._dataset = dataset
        instance._model.id = model.id
        instance._model.status = model.status

        return instance

    @property
    def _client(self) -> Optional["Argilla"]:
        if self._dataset:
            return self.dataset._client

    @property
    def _api(self) -> Optional["RecordsAPI"]:
        if self._client:
            return self._client.api.records


class RecordFields(dict):
    """This is a container class for the fields of a Record.
    It allows for accessing fields by attribute and key name.
    """

    def __init__(self, record: Record, fields: Optional[Dict[str, FieldValue]] = None) -> None:
        super().__init__(fields or {})
        self.record = record

    def to_dict(self) -> dict:
        return {key: cast_image(value) if self._is_image(key) else value for key, value in self.items()}

    def __getitem__(self, key: str) -> FieldValue:
        value = super().__getitem__(key)
        return uncast_image(value) if self._is_image(key) else value

    def _is_image(self, key: str) -> bool:
        if not self.record.dataset:
            return False
        return self.record.dataset.settings.schema[key].type == "image"


class RecordMetadata(dict):
    """This is a container class for the metadata of a Record."""

    def __init__(self, metadata: Optional[Dict[str, MetadataValue]] = None) -> None:
        super().__init__(metadata or {})

    def to_dict(self) -> dict:
        return dict(self.items())

    def api_models(self) -> List[MetadataModel]:
        return [MetadataModel(name=key, value=value) for key, value in self.items()]


class RecordVectors(dict):
    """This is a container class for the vectors of a Record.
    It allows for accessing suggestions by attribute and key name.
    """

    def __init__(self, vectors: Dict[str, VectorValue]) -> None:
        super().__init__(vectors or {})

    def to_dict(self) -> Dict[str, List[float]]:
        return dict(self.items())

    def api_models(self) -> List[VectorModel]:
        return [Vector(name=name, values=value).api_model() for name, value in self.items()]


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

    def __getitem__(self, name: str):
        return self.__responses_by_question_name[name]

    def __len__(self):
        return len(self.__responses)

    def __repr__(self) -> str:
        return {k: [{"value": v["value"]} for v in values] for k, values in self.to_dict().items()}.__repr__()

    def to_dict(self) -> Dict[str, List[Dict]]:
        """Converts the responses to a dictionary.
        Returns:
            A dictionary of responses.
        """
        response_dict = defaultdict(list)
        for response in self.__responses:
            response_dict[response.question_name].append({"value": response.value, "user_id": str(response.user_id)})
        return dict(response_dict)

    def api_models(self) -> List[UserResponseModel]:
        """Returns a list of ResponseModel objects."""

        responses_by_user_id = defaultdict(list)
        for response in self.__responses:
            responses_by_user_id[response.user_id].append(response)

        return [
            UserResponse(responses=responses, _record=self.record).api_model()
            for responses in responses_by_user_id.values()
        ]

    def add(self, response: Response) -> None:
        """Adds a response to the record and updates the record. Records can have multiple responses per question.
        Args:
            response: The response to add.
        """
        self._check_response_already_exists(response)

        response.record = self.record
        self.__responses.append(response)
        self.__responses_by_question_name[response.question_name].append(response)

    def _check_response_already_exists(self, response: Response) -> None:
        """Checks if a response for the same question name and user id already exists"""
        for existing_response in self.__responses_by_question_name[response.question_name]:
            if existing_response.user_id == response.user_id:
                raise ArgillaError(
                    f"Response for question with name {response.question_name!r} and user id {response.user_id!r} "
                    f"already found. The responses for the same question name do not support more than one user"
                )


class RecordSuggestions(Iterable[Suggestion]):
    """This is a container class for the suggestions of a Record.
    It allows for accessing suggestions by attribute and iterating over them.
    """

    def __init__(self, suggestions: List[Suggestion], record: Record) -> None:
        self.record = record
        self._suggestion_by_question_name: Dict[str, Suggestion] = {}
        suggestions = suggestions or []
        for suggestion in suggestions:
            suggestion.record = self.record
            self._suggestion_by_question_name[suggestion.question_name] = suggestion

    def __iter__(self):
        return iter(self._suggestion_by_question_name.values())

    def __getitem__(self, question_name: str):
        return self._suggestion_by_question_name[question_name]

    def __len__(self):
        return len(self._suggestion_by_question_name)

    def __repr__(self) -> str:
        return self.to_dict().__repr__()

    def to_dict(self) -> Dict[str, List[str]]:
        """Converts the suggestions to a dictionary.
        Returns:
            A dictionary of suggestions.
        """
        suggestion_dict = {}
        for question_name, suggestion in self._suggestion_by_question_name.items():
            suggestion_dict[question_name] = {
                "value": suggestion.value,
                "score": suggestion.score,
                "agent": suggestion.agent,
            }
        return suggestion_dict

    def api_models(self) -> List[SuggestionModel]:
        suggestions = self._suggestion_by_question_name.values()
        return [suggestion.api_model() for suggestion in suggestions]

    def add(self, suggestion: Suggestion) -> None:
        """Adds a suggestion to the record and updates the record. Records can have only one suggestion per question, so
        adding a new suggestion will overwrite the previous suggestion.
        Args:
            suggestion: The suggestion to add.
        """
        suggestion.record = self.record
        self._suggestion_by_question_name[suggestion.question_name] = suggestion
