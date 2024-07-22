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

from typing import Optional, List, Any, Union, Tuple

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
)


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
        elif field == "response.status":
            return ResponseFilterScopeModel(property="status")
        elif "metadata" in field:
            _, md_property = field.split(".")
            return MetadataFilterScopeModel(metadata_property=md_property)
        elif "suggestion" in field:
            question, _ = field.split(".")
            return SuggestionFilterScopeModel(question=question)
        elif "score" in field:
            question, _ = field.split(".")
            return SuggestionFilterScopeModel(question=question, property="score")
        elif "response" in field:
            question, _ = field.split(".")
            return ResponseFilterScopeModel(question=question)
        else:  # Question field -> Suggestion
            # TODO: The default path would be raise an error instead of consider suggestions by default
            #  (can be confusing)
            return SuggestionFilterScopeModel(question=field)


class Filter:
    """This class is used to map user filters to the internal filter models"""

    def __init__(self, conditions: Union[List[Tuple[str, str, Any]], Tuple[str, str, Any], None] = None):
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

    query: Optional[str] = None

    def __init__(self, *, query: Union[str, None] = None, filter: Union[Filter, None] = None):
        """Create a query object for use in Argilla search requests.add()

        Parameters:
            query (Union[str, None], optional): The query string that will be used to search.
            filter (Union[Filter, None], optional): The filter object that will be used to filter the search results.
        """

        self.query = query
        self.filter = filter

    def api_model(self) -> SearchQueryModel:
        model = SearchQueryModel()

        if self.query is not None:
            text_query = TextQueryModel(q=self.query)
            model.query = QueryModel(text=text_query)

        if self.filter is not None:
            model.filters = self.filter.api_model()

        return model


__all__ = ["Query", "Filter", "Condition"]
