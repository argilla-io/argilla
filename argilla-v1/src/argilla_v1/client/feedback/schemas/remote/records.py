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

import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from argilla_v1.client.feedback.schemas.enums import ResponseStatus
from argilla_v1.client.feedback.schemas.records import FeedbackRecord, ResponseSchema, SuggestionSchema
from argilla_v1.client.feedback.schemas.remote.shared import RemoteSchema
from argilla_v1.client.sdk.users.models import UserRole
from argilla_v1.client.sdk.v1.records import api as records_api_v1
from argilla_v1.client.sdk.v1.suggestions import api as suggestions_api_v1
from argilla_v1.client.utils import allowed_for_roles
from argilla_v1.pydantic_v1 import Field

if TYPE_CHECKING:
    import httpx

    from argilla_v1.client.sdk.v1.datasets.models import FeedbackResponseModel, FeedbackSuggestionModel
    from argilla_v1.client.sdk.v1.records.models import FeedbackRecordModel


class RemoteSuggestionSchema(SuggestionSchema, RemoteSchema):
    question_id: UUID

    class Config:
        validate_assignment = True
        allow_mutation = False

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self) -> None:
        """Deletes the `RemoteSuggestionSchema` from Argilla."""
        try:
            suggestions_api_v1.delete_suggestion(client=self.client, id=self.id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete suggestion with ID `{self.id}` from Argilla.") from e

    def to_local(self) -> "SuggestionSchema":
        """Converts the `RemoteSuggestionSchema` to a `SuggestionSchema`."""
        return SuggestionSchema(
            question_name=self.question_name,
            type=self.type,
            score=self.score,
            value=self.value,
            agent=self.agent,
        )

    @classmethod
    def from_api(
        cls,
        payload: "FeedbackSuggestionModel",
        question_id_to_name: Dict[UUID, str],
        client: Optional["httpx.Client"] = None,
    ) -> "RemoteSuggestionSchema":
        return RemoteSuggestionSchema(
            id=payload.id,
            client=client,
            question_id=payload.question_id,
            question_name=question_id_to_name[UUID(payload.question_id)],
            type=payload.type,
            score=payload.score,
            value=payload.value,
            agent=payload.agent,
        )


class RemoteResponseSchema(ResponseSchema, RemoteSchema):
    inserted_at: datetime
    updated_at: datetime

    def to_local(self) -> "ResponseSchema":
        """Converts the `RemoteResponseSchema` to a `ResponseSchema`."""
        return ResponseSchema(
            user_id=self.user_id,
            values=self.values,
            status=self.status,
        )

    @classmethod
    def from_api(cls, payload: "FeedbackResponseModel") -> "RemoteResponseSchema":
        return RemoteResponseSchema(
            user_id=payload.user_id,
            values=payload.values,
            status=ResponseStatus(payload.status),
            inserted_at=payload.inserted_at,
            updated_at=payload.updated_at,
        )


AllowedSuggestionSchema = Union[RemoteSuggestionSchema, SuggestionSchema]


class RemoteFeedbackRecord(FeedbackRecord, RemoteSchema):
    """Schema for the records of a `RemoteFeedbackDataset`.

    Note this schema shouldn't be instantiated directly, but just internally by the
    `RemoteFeedbackDataset` class when fetching records from Argilla.

    Args:
        question_name_to_id: A dictionary that maps the question names to their corresponding IDs.
        responses: A list of `RemoteResponseSchema` that contains the responses for the
            current record in Argilla. Every response is linked to only one user. Defaults
            to an empty list.
        suggestions: A list of `RemoteSuggestionSchema` that contains the suggestions
            for the current record in Argilla. Every suggestion is linked to only one
            question. Defaults to an empty list.
    """

    # TODO: remote record should receive a dataset instead of this
    question_name_to_id: Optional[Dict[str, UUID]] = Field(..., exclude=True, repr=False)

    responses: List[RemoteResponseSchema] = Field(default_factory=list)
    suggestions: Union[Tuple[AllowedSuggestionSchema], List[AllowedSuggestionSchema]] = Field(default_factory=tuple)

    class Config:
        allow_mutation = True
        validate_assignment = True

    def __normalize_suggestions_to_update(
        self,
        suggestions: Union[
            Dict[str, Any], List[Dict[str, Any]], AllowedSuggestionSchema, List[AllowedSuggestionSchema]
        ],
    ) -> List[AllowedSuggestionSchema]:
        if isinstance(suggestions, (dict, SuggestionSchema)):
            suggestions = [suggestions]

        new_suggestions = {}

        for suggestion in suggestions:
            if isinstance(suggestion, dict):
                if "id" in suggestion:
                    if "question_id" not in suggestion or not suggestion["question_id"]:
                        suggestion["question_id"] = self.question_name_to_id[suggestion["question_name"]]
                    suggestion = RemoteSuggestionSchema(client=self.client, **suggestion)
                else:
                    suggestion = SuggestionSchema(**suggestion)

            if suggestion.question_name in new_suggestions:
                warnings.warn(
                    f"A suggestion for question `{suggestion.question_name}` has been"
                    " provided twice in the same update, so the last one will be the one"
                    " to be kept.",
                    UserWarning,
                    stacklevel=1,
                )

            new_suggestions[suggestion.question_name] = suggestion

        return list(new_suggestions.values())

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def update(
        self,
        suggestions: Optional[
            Union[
                SuggestionSchema,
                Dict[str, Any],
                List[SuggestionSchema],
                List[Dict[str, Any]],
            ]
        ] = None,
    ) -> None:
        """Update a `RemoteFeedbackRecord` in Argilla.

        Note that this method will update the record in Argilla directly.

        Args:
            suggestions: **DEPRECATED** the new list of suggestions to set for the
                record. It can be a single `SuggestionSchema`, a list of `SuggestionSchema`,
                a single dictionary or a list of dictionary. If a dictionary is provided,
                it will be converted to a `SuggestionSchema` internally. Defaults to
                `None`.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
        """
        if suggestions is not None:
            warnings.warn(
                "The `suggestions` argument is deprecated and will be removed in "
                "future releases. In order to update the suggestions of a record "
                "assign the `suggestions` attribute directly.",
                DeprecationWarning,
                stacklevel=1,
            )

            new_suggestions = self.__normalize_suggestions_to_update(suggestions)
            self.suggestions = tuple(new_suggestions)

        self.__updated_record_data()

    def __updated_record_data(self) -> None:
        response = records_api_v1.update_record(self.client, self.id, self.to_server_payload(self.question_name_to_id))

        updated_record = self.from_api(
            payload=response.parsed,
            question_id_to_name={value: key for key, value in self.question_name_to_id.items()}
            if self.question_name_to_id
            else None,
            client=self.client,
        )

        self.__dict__.update(updated_record.__dict__)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete_suggestions(self, suggestions: Union[RemoteSuggestionSchema, List[RemoteSuggestionSchema]]) -> None:
        """Deletes the provided suggestions from the record in Argilla. Note that the
        suggestions must exist in Argilla to be removed from the record.

        Args:
            suggestions: can be a single `RemoteSuggestionSchema` or a list of
                `RemoteSuggestionSchema`.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.

        **DEPRECATED**
        """

        warnings.warn(
            "The `delete_suggestions` method is deprecated and will be removed in "
            "future releases. In order to update/delete the suggestions of a record "
            "assign the `suggestions` attribute directly (`record.suggestions = []`).",
            DeprecationWarning,
            stacklevel=1,
        )

        if isinstance(suggestions, RemoteSuggestionSchema):
            suggestions = [suggestions]

        existing_suggestions = {suggestion.question_name: suggestion for suggestion in self.suggestions}
        delete_suggestions = []
        for suggestion in suggestions:
            if suggestion.question_name not in existing_suggestions:
                warnings.warn(
                    f"A suggestion for question `{suggestion.question_name}` has not been"
                    " provided, so it cannot be removed.",
                    UserWarning,
                    stacklevel=1,
                )
            else:
                existing_suggestions.pop(suggestion.question_name, None)
                delete_suggestions.append(suggestion)

        try:
            records_api_v1.delete_suggestions(
                client=self.client, id=self.id, suggestion_ids=[suggestion.id for suggestion in delete_suggestions]
            )
            self.__dict__["suggestions"] = tuple(existing_suggestions.values())
        except Exception as e:
            raise RuntimeError(
                f"Failed to delete suggestions with IDs `{[suggestion.id for suggestion in delete_suggestions]}` from "
                f"record with ID `{self.id}` from Argilla."
            ) from e

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self) -> FeedbackRecord:
        """Deletes the `RemoteFeedbackRecord` from Argilla.

        Returns:
            The deleted record formatted as a `FeedbackRecord`.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
        """
        try:
            response = records_api_v1.delete_record(client=self.client, id=self.id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete record with ID `{self.id}` from Argilla.") from e
        return RemoteFeedbackRecord.from_api(
            payload=response.parsed, question_id_to_name={value: key for key, value in self.question_name_to_id.items()}
        ).to_local()

    def to_local(self) -> "FeedbackRecord":
        """Converts the `RemoteFeedbackRecord` to a `FeedbackRecord`."""
        return FeedbackRecord(
            fields=self.fields,
            responses=[response.to_local() for response in self.responses],
            suggestions=[suggestion.to_local() for suggestion in self.suggestions],
            metadata=self.metadata,
            vectors=self.vectors,
            external_id=self.external_id,
        )

    @classmethod
    def from_api(
        cls,
        payload: "FeedbackRecordModel",
        question_id_to_name: Dict[UUID, str],
        client: Optional["httpx.Client"] = None,
    ) -> "RemoteFeedbackRecord":
        return RemoteFeedbackRecord(
            id=payload.id,
            client=client,
            fields=payload.fields,
            responses=[RemoteResponseSchema.from_api(response) for response in payload.responses]
            if payload.responses
            else [],
            suggestions=[
                RemoteSuggestionSchema.from_api(suggestion, question_id_to_name=question_id_to_name, client=client)
                for suggestion in payload.suggestions
            ]
            if payload.suggestions
            else [],
            metadata=payload.metadata if payload.metadata else {},
            vectors=payload.vectors if payload.vectors else {},
            external_id=payload.external_id if payload.external_id else None,
            question_name_to_id={value: key for key, value in question_id_to_name.items()},
        )
