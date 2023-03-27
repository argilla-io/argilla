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
import logging
import re
from enum import Enum
from typing import Any, Dict, List, Optional

from luqum.elasticsearch import ElasticsearchQueryBuilder, SchemaAnalyzer
from luqum.parser import parser

from argilla.server.daos.backend.query_helpers import filters
from argilla.server.daos.backend.search.model import (
    BackendDatasetsQuery,
    BackendQuery,
    BackendRecordsQuery,
    BaseDatasetsQuery,
    QueryRange,
    SortableField,
    SortConfig,
)


class HighlightParser:
    _SEARCH_KEYWORDS_FIELD = "search_keywords"

    __HIGHLIGHT_PRE_TAG__ = "<@@-ar-key>"
    __HIGHLIGHT_POST_TAG__ = "</@@-ar-key>"
    __HIGHLIGHT_VALUES_REGEX__ = re.compile(rf"{__HIGHLIGHT_PRE_TAG__}(.+?){__HIGHLIGHT_POST_TAG__}")

    __HIGHLIGHT_PHRASE_PRE_PARSER_REGEX__ = re.compile(rf"{__HIGHLIGHT_POST_TAG__}\s+{__HIGHLIGHT_PRE_TAG__}")

    @property
    def search_keywords_field(self) -> str:
        return self._SEARCH_KEYWORDS_FIELD

    @classmethod
    def build_query_highlight(cls):
        return {
            "pre_tags": [cls.__HIGHLIGHT_PRE_TAG__],
            "post_tags": [cls.__HIGHLIGHT_POST_TAG__],
            "require_field_match": True,
            "fields": {
                "text": {},
                "text.*": {},
                "inputs.*": {},
            },
        }

    @classmethod
    def parse_highligth_results(
        cls,
        doc: Dict[str, Any],
        is_phrase_query: bool = False,
    ) -> Optional[List[str]]:
        highlight_info = doc.get("highlight")
        if not highlight_info:
            return None

        search_keywords = []
        for content in highlight_info.values():
            if not isinstance(content, list):
                content = [content]
            text = " ".join(content)

            if is_phrase_query:
                text = re.sub(
                    pattern=cls.__HIGHLIGHT_PHRASE_PRE_PARSER_REGEX__,
                    repl=" ",
                    string=text,
                )
            search_keywords.extend(
                re.findall(
                    pattern=cls.__HIGHLIGHT_VALUES_REGEX__,
                    string=text,
                )
            )
        return list(set(search_keywords))


class EsQueryBuilder:
    _INSTANCE: "EsQueryBuilder" = None
    _LOGGER = logging.getLogger(__name__)

    @classmethod
    def get_instance(cls):
        if not cls._INSTANCE:
            cls._INSTANCE = cls()
        return cls._INSTANCE

    def _datasets_to_es_query(self, query: Optional[BackendDatasetsQuery] = None) -> Dict[str, Any]:
        if not query:
            return filters.match_all()

        query_filters = []
        if query.workspaces:
            query_filters.append(
                filters.boolean_filter(
                    should_filters=[
                        filters.terms_filter("owner.keyword", query.workspaces),  # backward comp.
                        filters.terms_filter("workspace.keyword", query.workspaces),
                    ]
                )
            )

        if query.tasks:
            query_filters.append(
                filters.terms_filter(
                    field="task.keyword",
                    values=query.tasks,
                )
            )
        if query.name:
            query_filters.append(
                filters.term_filter(
                    field="name.keyword",
                    value=query.name,
                )
            )
        if not query_filters:
            return filters.match_all()

        return filters.boolean_filter(
            should_filters=query_filters,
            minimum_should_match=len(query_filters),
        )

    def _search_to_es_query(
        self,
        schema: Optional[Dict[str, Any]] = None,
        query: Optional[BackendRecordsQuery] = None,
        sort: Optional[SortConfig] = None,
    ):
        if not query:
            return filters.match_all()

        if not query.advanced_query_dsl or not query.query_text:
            return self._to_es_query(query)

        text_search = query.query_text
        new_query = query.copy(update={"query_text": None})

        schema = SchemaAnalyzer(schema)
        es_query_builder = ElasticsearchQueryBuilder(
            **{
                **schema.query_builder_options(),
                "default_field": "text",
            }
        )

        query_tree = parser.parse(text_search)
        query_text = es_query_builder(query_tree)
        boolean_filter_query = self._to_es_query(new_query)
        return filters.boolean_filter(
            filter_query=boolean_filter_query,
            must_query=query_text,
        )

    def map_2_es_query(
        self,
        schema: Dict[str, Any],
        query: BackendQuery,
        sort: SortConfig = SortConfig(),
        exclude_fields: Optional[List[str]] = None,
        include_fields: List[str] = None,
        doc_from: Optional[int] = None,
        highlight: Optional[HighlightParser] = None,
        size: Optional[int] = None,
        search_after_param: Optional[Any] = None,
    ) -> Dict[str, Any]:
        if query and query.raw_query:
            es_query = {"query": query.raw_query}
        else:
            es_query: Dict[str, Any] = (
                {"query": self._datasets_to_es_query(query)}
                if isinstance(query, BaseDatasetsQuery)
                else {"query": self._search_to_es_query(schema, query)}
            )

        if search_after_param:
            es_query["search_after"] = search_after_param

        if sort.shuffle:
            self._setup_random_score(es_query)
        else:
            es_sort = self.map_2_es_sort_configuration(schema=schema, sort=sort)
            if es_sort:
                es_query["sort"] = es_sort

        if doc_from:
            es_query["from"] = doc_from

        source = {}
        if exclude_fields:
            source.update({"excludes": exclude_fields})
        if include_fields:
            source.update({"includes": include_fields})
        if source:
            es_query["_source"] = source

        if highlight and (
            not include_fields
            # Enable highlight when requesting ALL fields
            # or specific request the search_keywords one
            or "*" in include_fields
            or highlight.search_keywords_field in include_fields
        ):
            es_query["highlight"] = highlight.build_query_highlight()

        if hasattr(query, "vector") and query.vector is not None:
            self._build_knn_configuration(
                es_query=es_query,
                vector_field=self.get_vector_field_name(query.vector.name),
                vector_value=query.vector.value,
                top_k=query.vector.k or size,
            )

        return es_query

    def map_2_es_sort_configuration(self, schema: Dict[str, Any], sort: SortConfig) -> Optional[List[Dict[str, Any]]]:
        if not sort.sort_by or sort.shuffle:
            return None

        # TODO(@frascuchon): compute valid list from the schema
        valid_fields = sort.valid_fields or [
            "id",
            "metadata",
            "score",
            "predicted",
            "predicted_as",
            "predicted_by",
            "annotated_as",
            "annotated_by",
            "status",
            "last_updated",
            "event_timestamp",
        ]

        id_field = "id"
        id_keyword_field = "id.keyword"
        schema = schema or {}
        mappings = self._clean_mappings(schema.get("mappings", {}))
        use_id_keyword = "text" == mappings.get("id")

        es_sort = []
        for sortable_field in sort.sort_by or [SortableField(id="id")]:
            if valid_fields:
                if sortable_field.id.split(".")[0] not in valid_fields:
                    raise AssertionError(
                        f"Wrong sort id {sortable_field.id}. Valid values are: " f"{[str(v) for v in valid_fields]}"
                    )
            field = sortable_field.id
            if field == id_field and use_id_keyword:
                field = id_keyword_field
            es_sort.append({field: {"order": sortable_field.order}})

        return es_sort

    @classmethod
    def _to_es_query(cls, query: BackendRecordsQuery) -> Dict[str, Any]:
        if query.ids:
            return filters.ids_filter(query.ids)

        query_text = filters.text_query(query.query_text)
        all_filters = filters.metadata(query.metadata)
        if query.has_annotation:
            all_filters.append(filters.exists_field("annotated_by"))
        if query.has_prediction:
            all_filters.append(filters.exists_field("predicted_by"))

        query_data = query.dict(
            exclude={
                "advanced_query_dsl",
                "vector",
                "query_text",
                "metadata",
                "uncovered_by_rules",
                "has_annotation",
                "has_prediction",
            }
        )
        for key, value in query_data.items():
            if value is None:
                continue
            key_filter = None
            if isinstance(value, dict):
                value = getattr(query, key)  # check the original field type
            if isinstance(value, list):
                key_filter = filters.terms_filter(key, value)
            elif isinstance(value, (str, Enum)):
                key_filter = filters.term_filter(key, value)
            elif isinstance(value, QueryRange):
                key_filter = filters.range_filter(field=key, value_from=value.range_from, value_to=value.range_to)

            else:
                cls._LOGGER.warning(f"Cannot parse query value {value} for key {key}")
            if key_filter:
                all_filters.append(key_filter)

        boolean_filter_query = filters.boolean_filter(
            must_query=query_text or filters.match_all(),
            filter_query=filters.boolean_filter(
                should_filters=all_filters,
                minimum_should_match=len(all_filters),
            )
            if all_filters
            else None,
            must_not_query=filters.boolean_filter(
                should_filters=[filters.text_query(q) for q in query.uncovered_by_rules]
            )
            if hasattr(query, "uncovered_by_rules") and query.uncovered_by_rules
            else None,
        )

        return boolean_filter_query

    def _clean_mappings(self, mappings: Dict[str, Any]):
        if not mappings:
            return {}

        return {
            key: definition.get("type") or self._clean_mappings(definition)
            for key, definition in mappings["properties"].items()
        }

    def _build_knn_configuration(
        self,
        *,
        es_query: Dict[str, Any],
        vector_field: str,
        vector_value: List[float],
        top_k: Optional[int] = None,
    ):
        def compute_num_candidates(k: int):
            if k < 50:
                return 500
            if 50 <= k < 200:
                return 100
            if 200 <= k < 500:
                return 2000
            # > 500
            return 2500

        top_k = top_k or 5
        num_candidates = compute_num_candidates(top_k)

        es_query_filter = es_query["query"]

        es_query["knn"] = {
            "field": vector_field,
            "query_vector": vector_value,
            "k": top_k,  # TODO: parameterize
            "num_candidates": num_candidates,  # TODO: parameterize
            "filter": es_query_filter,
        }
        es_query.pop("sort", None)
        del es_query["query"]

    def _setup_random_score(self, es_query: Dict[str, Any]):
        query = es_query["query"]
        es_query["query"] = {
            "function_score": {
                "query": query,
                "random_score": {},
            }
        }
        return es_query

    def get_vector_field_name(self, vector_name: str) -> str:
        return f"vectors.{vector_name}.value"


class OpenSearchQueryBuilder(EsQueryBuilder):
    def _build_knn_configuration(
        self,
        *,
        es_query: Dict[str, Any],
        vector_field: str,
        vector_value: List[float],
        top_k: Optional[int] = None,
    ):
        top_k = top_k or 5
        knn = {
            vector_field: {
                "vector": vector_value,
                "k": top_k,  # TODO: Input from query
            }
        }
        es_query.pop("sort", None)
        filter = es_query.pop("query")
        es_query.update(
            {
                "query": {"knn": knn},
                "post_filter": filter,
            }
        )
