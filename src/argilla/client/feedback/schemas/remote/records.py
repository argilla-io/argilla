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
from typing import Any, Dict, List, Tuple, Union
from uuid import UUID

import httpx
from pydantic import Field

from argilla.client.feedback.schemas.records import FeedbackRecord, SuggestionSchema
from argilla.client.sdk.users.models import UserRole
from argilla.client.sdk.v1.datasets import api as datasets_api_v1
from argilla.client.sdk.v1.records import api as records_api_v1
from argilla.client.sdk.v1.suggestions import api as suggestions_api_v1
from argilla.client.utils import allowed_for_roles


class RemoteSuggestionSchema(SuggestionSchema):
    client: httpx.Client
    id: UUID
    question_id: UUID

    # TODO(alvarobartt): here to be able to use the `allowed_for_roles` decorator
    @property
    def _client(self) -> httpx.Client:
        return self.client

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete(self) -> None:
        """Deletes the `RemoteSuggestionSchema` from Argilla."""
        try:
            suggestions_api_v1.delete_suggestion(client=self._client, id=self.id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete suggestion with ID `{self.id}` from Argilla.") from e

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        allow_mutation = False
        exclude = {"client"}


class RemoteFeedbackRecord(FeedbackRecord):
    """Schema for the records of a `RemoteFeedbackDataset`.

    Note this schema shouldn't be instantiated directly, but just internally by the
    `RemoteFeedbackDataset` class when fetching records from Argilla.

    Args:
        client: The Argilla client to use to push the record to Argilla. Is shared with
            the `RemoteFeedbackDataset` that created this record.
        name2id: A dictionary that maps the question names to their corresponding IDs.
        id: The ID of the record in Argilla. Defaults to None, and is automatically
            fulfilled internally once the record is pushed to Argilla.
        suggestions: A list of `RemoteSuggestionSchema` that contains the suggestions
            for the current record in Argilla. Every suggestion is linked to only one
            question. Defaults to an empty list.
    """

    client: httpx.Client
    name2id: Dict[str, UUID]

    id: UUID
    suggestions: Union[Tuple[RemoteSuggestionSchema], List[RemoteSuggestionSchema]] = Field(
        default_factory=tuple, allow_mutation=False
    )

    # TODO(alvarobartt): here to be able to use the `allowed_for_roles` decorator
    @property
    def _client(self) -> httpx.Client:
        return self.client

    def __update_suggestions(
        self,
        suggestions: Union[
            RemoteSuggestionSchema,
            List[RemoteSuggestionSchema],
            SuggestionSchema,
            List[SuggestionSchema],
            Dict[str, Any],
            List[Dict[str, Any]],
        ],
    ) -> None:
        """Updates the suggestions for the record in Argilla. Note that the suggestions
        must exist in Argilla to be updated.

        Note that this method will update the record in Argilla directly.

        Args:
            suggestions: can be a single `RemoteSuggestionSchema` or `SuggestionSchema`,
                a list of `RemoteSuggestionSchema` or `SuggestionSchema`, a single
                dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `RemoteSuggestionSchema` internally.
        """
        if isinstance(suggestions, (dict, SuggestionSchema)):
            suggestions = [suggestions]

        existing_suggestions = {suggestion.question_name: suggestion for suggestion in self.suggestions}
        new_suggestions = {}

        for suggestion in suggestions:
            if isinstance(suggestion, dict):
                if "question_id" not in suggestion or not suggestion["question_id"]:
                    suggestion["question_id"] = self.name2id[suggestion["question_name"]]
                if "id" in suggestion:
                    suggestion = RemoteSuggestionSchema(client=self._client, **suggestion)
                else:
                    suggestion = SuggestionSchema(**suggestion)

            if isinstance(suggestion, SuggestionSchema):
                if not suggestion.question_id:
                    suggestion.question_id = self.name2id[suggestion.question_name]

            if suggestion.question_name in new_suggestions:
                warnings.warn(
                    f"A suggestion for question `{suggestion.question_name}` has been"
                    " provided twice in the same update, so the last one will be the one"
                    " to be kept.",
                    UserWarning,
                    stacklevel=1,
                )
                new_suggestions.pop(suggestion.question_name, None)
                new_suggestions[suggestion.question_name] = suggestion
            elif suggestion.question_name in existing_suggestions:
                comparable_fields = {"question_name", "type", "score", "value", "agent"}
                comparable_suggestion = suggestion.dict(include={"question_name", "type", "score", "value", "agent"})
                if any(
                    [
                        comparable_suggestion == suggestion.dict(include=comparable_fields)
                        for suggestion in existing_suggestions.values()
                    ]
                ):
                    warnings.warn(
                        f"A suggestion for question `{suggestion.question_name}` has already"
                        " been provided and the provided suggestion is the same, so it will"
                        " be ignored.",
                        UserWarning,
                        stacklevel=1,
                    )
                else:
                    warnings.warn(
                        f"A suggestion for question `{suggestion.question_name}` has already"
                        " been provided but the provided suggestion is different, so it will"
                        " overwrite the existing one.",
                        UserWarning,
                        stacklevel=1,
                    )
                    existing_suggestions.pop(suggestion.question_name, None)
                    new_suggestions[suggestion.question_name] = suggestion
            else:
                new_suggestions[suggestion.question_name] = suggestion

        for suggestion in new_suggestions.values():
            if isinstance(suggestion, SuggestionSchema):
                exclude = {"question_name"}
            elif isinstance(suggestion, RemoteSuggestionSchema):
                exclude = {"client", "id", "question_name"}
            pushed_suggestion = datasets_api_v1.set_suggestion(
                client=self._client, record_id=self.id, **suggestion.dict(exclude_none=True, exclude=exclude)
            )
            existing_suggestions[suggestion.question_name] = RemoteSuggestionSchema(
                client=self._client,
                question_name=suggestion.question_name,
                **pushed_suggestion.parsed.dict(exclude_none=True),
            )

        self.__dict__["suggestions"] = tuple(existing_suggestions.values())

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def update(
        self,
        suggestions: Union[
            RemoteSuggestionSchema,
            List[RemoteSuggestionSchema],
            SuggestionSchema,
            List[SuggestionSchema],
            Dict[str, Any],
            List[Dict[str, Any]],
        ],
    ) -> None:
        """Update a `RemoteFeedbackRecord`. Currently just `suggestions` are supported.

        Note that this method will update the record in Argilla directly.

        Args:
            suggestions: can be a single `RemoteSuggestionSchema` or `SuggestionSchema`,
                a list of `RemoteSuggestionSchema` or `SuggestionSchema`, a single
                dictionary, or a list of dictionaries. If a dictionary is provided,
                it will be converted to a `RemoteSuggestionSchema` internally.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
        """
        self.__update_suggestions(suggestions=suggestions)

    @allowed_for_roles(roles=[UserRole.owner, UserRole.admin])
    def delete_suggestions(self, suggestions: Union[RemoteSuggestionSchema, List[RemoteSuggestionSchema]]) -> None:
        """Deletes the provided suggestions from the record in Argilla. Note that the
        suggestions must exist in Argilla to be removed from the record.

        Args:
            suggestions: can be a single `RemoteSuggestionSchema` or a list of
                `RemoteSuggestionSchema`.

        Raises:
            PermissionError: if the user does not have either `owner` or `admin` role.
        """
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
                client=self._client, id=self.id, suggestion_ids=[suggestion.id for suggestion in delete_suggestions]
            )
            self.__dict__["suggestions"] = tuple(existing_suggestions.values())
        except Exception as e:
            raise RuntimeError(
                f"Failed to delete suggestions with IDs `{[suggestion.id for suggestion in delete_suggestions]}` from record with ID `{self.id}` from Argilla."
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
            response = records_api_v1.delete_record(client=self._client, id=self.id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete record with ID `{self.id}` from Argilla.") from e
        return FeedbackRecord(**response.parsed.dict(exclude={"id", "inserted_at", "updated_at"}, exclude_none=True))

    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        exclude = {"_unified_responses", "client", "name2id"}
