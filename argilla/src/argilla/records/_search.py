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
from typing import List, Any, Union, Tuple, Iterable, TYPE_CHECKING

from argilla._models import SearchQueryModel
from argilla._models._search import (
    TextQueryModel,
    ResponseFilterScopeModel,
    SuggestionFilterScopeModel,
    MetadataFilterScopeModel,
    ScopeModel,
    RangeFilterModel,
    TermsFilterModel,
    FilterModel,
    AndFilterModel,
    QueryModel,
    RecordFilterScopeModel,
    VectorQueryModel,
)

if TYPE_CHECKING:
    from argilla.records import Record

__all__ = ["Query", "Filter", "Condition", "Similar", "Conditions"]


class Condition(Tuple[str, str, Any]):
    """This class is used to map user conditions to the internal filter models"""

    def api_model(self) -> FilterModel:
        field, operator, value = self

        field = field.strip()
        scope = self._extract_filter_scope(field)

        operator = operator.strip()
        if operator == "==":
            return TermsFilterModel(values=[value], scope=scope)
        elif operator == "in":
            return TermsFilterModel(values=value, scope=scope)
        elif operator in [">="]:
            return RangeFilterModel(ge=value, scope=scope)
        elif operator == "<=":
            return RangeFilterModel(le=value, scope=scope)
        else:
            raise ValueError(f"Unknown operator: {operator}")

    @staticmethod
    def _extract_filter_scope(field: str) -> ScopeModel:
        field = field.strip()
        if field == "status":
            return RecordFilterScopeModel(property="status")
        elif field == "id":
            return RecordFilterScopeModel(property="external_id")
        elif field == "_server_id":
            return RecordFilterScopeModel(property="id")
        elif field == "inserted_at":
            return RecordFilterScopeModel(property="inserted_at")
        elif field == "updated_at":
            return RecordFilterScopeModel(property="updated_at")
        elif field == "response.status":
            return ResponseFilterScopeModel(property="status")
        elif field.startswith("metadata"):
            _, md_property = field.split(".")
            return MetadataFilterScopeModel(metadata_property=md_property)
        elif field.endswith("suggestion"):
            question, _ = field.split(".")
            return SuggestionFilterScopeModel(question=question)
        elif field.endswith("score"):
            question, _ = field.split(".")
            return SuggestionFilterScopeModel(question=question, property="score")
        elif field.endswith("agent"):
            question, _ = field.split(".")
            return SuggestionFilterScopeModel(question=question, property="agent")
        elif field.endswith("type"):
            question, _ = field.split(".")
            return SuggestionFilterScopeModel(question=question, property="type")
        elif field.endswith("response"):
            question, _ = field.split(".")
            return ResponseFilterScopeModel(question=question)
        else:  # Question field -> Suggestion
            # TODO: Return None and skip this filter
            return SuggestionFilterScopeModel(question=field)


Conditions = Union[List[Tuple[str, str, Any]], Tuple[str, str, Any]]


class Similar:
    """This class is used to map user similar queries to the internal query models"""

    def __init__(self, name: str, value: Union[Iterable[float], "Record"], most_similar: bool = True):
        """
        Create a similar object for use in Argilla search requests.

        Parameters:
            name: The name of the vector field
            value: The vector value or the record to search for similar records
            most_similar: Whether to search for the most similar records or the least similar records
        """

        self.name = name
        self.value = value
        self.most_similar = most_similar if most_similar is not None else True

    def api_model(self) -> VectorQueryModel:
        from argilla.records import Record

        order = "most_similar" if self.most_similar else "least_similar"

        if isinstance(self.value, Record):
            return VectorQueryModel(name=self.name, record_id=self.value._server_id, order=order)

        return VectorQueryModel(name=self.name, value=self.value, order=order)


class Filter:
    """This class is used to map user filters to the internal filter models"""

    def __init__(self, conditions: Union[Conditions, None] = None):
        """ Create a filter object for use in Argilla search requests.

        Parameters:
            conditions (Union[List[Tuple[str, str, Any]], Tuple[str, str, Any], None], optional): \
                The conditions that will be used to filter the search results. \
                The conditions should be a list of tuples where each tuple contains \
                the field, operator, and value. For example `("label", "in", ["positive","happy"])`.\
        """

        if isinstance(conditions, tuple):
            conditions = [conditions]
        self.conditions = [Condition(condition) for condition in conditions]

    def api_model(self) -> AndFilterModel:
        return AndFilterModel.model_validate({"and": [condition.api_model() for condition in self.conditions]})


class Query:
    """This class is used to map user queries to the internal query models"""

    def __init__(
        self,
        *,
        query: Union[str, None] = None,
        similar: Union[Similar, None] = None,
        filter: Union[Filter, Conditions, None] = None,
    ):
        """Create a query object for use in Argilla search requests.add()

        Parameters:
            query (Union[str, None], optional): The query string that will be used to search.
            similar (Union[Similar, None], optional): The similar object that will be used to search for similar records
            filter (Union[Filter, None], optional): The filter object that will be used to filter the search results.
        """

        if isinstance(filter, tuple):
            filter = [filter]

        if isinstance(filter, list):
            filter = Filter(conditions=filter)

        self.query = query
        self.filter = filter
        self.similar = similar

    def has_search(self) -> bool:
        return bool(self.query or self.similar or self.filter)

    def api_model(self) -> SearchQueryModel:
        model = SearchQueryModel()

        if self.query or self.similar:
            query = QueryModel()

            if self.query is not None:
                query.text = TextQueryModel(q=self.query)

            if self.similar is not None:
                query.vector = self.similar.api_model()

            model.query = query

        if self.filter is not None:
            model.filters = self.filter.api_model()

        return model
