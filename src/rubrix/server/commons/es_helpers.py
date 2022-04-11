#  coding=utf-8
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

import math
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from rubrix.server.tasks.commons import SortableField, TaskStatus
from rubrix.server.tasks.commons.api import EsRecordDataFieldNames
from rubrix.server.tasks.commons.dao.es_config import mappings


def nested_mappings_from_base_model(model_class: Type[BaseModel]) -> Dict[str, Any]:
    def resolve_mapping(info) -> Dict[str, Any]:
        the_type = info.get("type")
        if the_type == "number":
            return {"type": "float"}
        if the_type == "integer":
            return {"type": "integer"}
        return mappings.keyword_field(enable_text_search=True)

    return {
        "type": "nested",
        "include_in_root": True,
        "properties": {
            key: resolve_mapping(info)
            for key, info in model_class.schema()["properties"].items()
        },
    }


def sort_by2elasticsearch(
    sort: List[SortableField], valid_fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    valid_fields = valid_fields or []
    result = []
    for sortable_field in sort:
        if valid_fields:
            assert sortable_field.id.split(".")[0] in valid_fields, (
                f"Wrong sort id {sortable_field.id}. Valid values are: "
                f"{[str(v) for v in valid_fields]}"
            )
        result.append({sortable_field.id: {"order": sortable_field.order}})
    return result


def parse_aggregations(
    es_aggregations: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """Transforms elasticsearch raw aggregations into a more friendly structure"""

    if es_aggregations is None:
        return None

    def is_extended_stats_aggregation(aggr_data) -> bool:
        for metric in [
            "count",
            "min",
            "max",
            "avg",
            "sum",
            "variance",
            "std_deviation",
        ]:
            if metric not in aggr_data:
                return False
        return True

    def parse_buckets(buckets: List[Dict[str, Any]]) -> Dict[str, Any]:
        parsed = {}
        for bucket in buckets:
            key, key_as_string, doc_count, meta, _from, _to = (
                bucket.pop("key", None),
                bucket.pop("key_as_string", None),
                bucket.pop("doc_count", 0),
                bucket.pop("meta", None),
                bucket.pop("from", None),
                bucket.pop("to", None),
            )
            if len(bucket) == 1 and not (_from or _to):
                k = [k for k in bucket][0]
                parsed.update({key or k: parse_buckets(bucket[k].get("buckets", []))})
            elif len(bucket) > 1:
                key_metrics = {}
                for metric_key, metric in list(bucket.items()):
                    if "buckets" in metric:
                        key_metrics.update(
                            {metric_key: parse_buckets(metric.get("buckets", []))}
                        )
                    else:
                        metric_values = list(metric.values())
                        value = metric_values[0] if len(metric_values) == 1 else metric
                        key_metrics[metric_key] = value
                parsed.update({key: key_metrics})
            elif key is not None:
                parsed.update({key_as_string or key: doc_count})
        return parsed

    result = {}
    for key, values in es_aggregations.items() or {}:
        if "buckets" in values:
            buckets = values["buckets"]
            if isinstance(buckets, dict):
                buckets = [{"key": k, **v} for k, v in buckets.items()]
            result[key] = parse_buckets(buckets)
        elif is_extended_stats_aggregation(values):
            result[key] = {"rubrix:stats": values}  # statistical aggregations
        else:
            result[key] = list(parse_buckets([values]).values())[0]
    return result


def decode_field_name(field: EsRecordDataFieldNames) -> str:
    return field.value


class filters:
    """Group of functions related to elasticsearch filters"""

    @staticmethod
    def boolean_filter(
        filter_query: Optional[Dict[str, Any]] = None,
        must_query: Optional[Dict[str, Any]] = None,
        must_not_query: Optional[Dict[str, Any]] = None,
        should_filters: Optional[List[Dict[str, Any]]] = None,
        minimum_should_match: Union[int, str] = 1,
    ):
        es_query = {}

        if filter_query:
            es_query["filter"] = filter_query

        if must_query:
            es_query["must"] = must_query

        if must_not_query:
            es_query["must_not"] = must_not_query

        if should_filters:
            es_query["should"] = should_filters
            es_query["minimum_should_match"] = minimum_should_match or 1

        if not es_query:
            raise ValueError("Must provide minimal data for boolean query")

        return {"bool": es_query}

    @staticmethod
    def exists_field(field_name: str) -> Dict[str, Any]:
        """Filter records containing task info for given task name"""
        return {"exists": {"field": field_name}}

    @staticmethod
    def predicted_by(predicted_by: List[str] = None) -> Optional[Dict[str, Any]]:
        """Filter records with given predicted by terms"""

        if not predicted_by:
            return None
        return {
            "terms": {
                decode_field_name(EsRecordDataFieldNames.predicted_by): predicted_by
            }
        }

    @staticmethod
    def annotated_by(annotated_by: List[str] = None) -> Optional[Dict[str, Any]]:
        """Filter records with given predicted by terms"""
        if not annotated_by:
            return None
        return {
            "terms": {
                decode_field_name(EsRecordDataFieldNames.annotated_by): annotated_by
            }
        }

    @staticmethod
    def status(status: List[TaskStatus] = None) -> Optional[Dict[str, Any]]:
        """Filter records by status"""
        if not status:
            return None
        return {"terms": {decode_field_name(EsRecordDataFieldNames.status): status}}

    @staticmethod
    def metadata(metadata: Dict[str, Union[str, List[str]]]) -> List[Dict[str, Any]]:
        """Filter records by compound metadata"""
        if not metadata:
            return []

        return [
            {
                "terms": {
                    f"metadata.{key}": query_text
                    if isinstance(query_text, List)
                    else [query_text]
                }
            }
            for key, query_text in metadata.items()
        ]

    @staticmethod
    def terms_filter(field: str, values: List[Any]) -> Optional[Dict[str, Any]]:
        if not values:
            return None
        return {"terms": {field: values}}

    @staticmethod
    def term_filter(field: str, value: Any) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        return {"term": {field: value}}

    @staticmethod
    def range_filter(
        field: str, value_from: Optional[Any] = None, value_to: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        filter_data = {}
        if value_from is not None:
            filter_data["gte"] = value_from
        if value_to is not None:
            filter_data["lte"] = value_to
        if not filter_data:
            return None
        return {"range": {field: filter_data}}

    @staticmethod
    def text_query(text_query: Optional[str]) -> Dict[str, Any]:
        """Filter records matching text query"""
        if text_query is None:
            return filters.match_all()
        return filters.boolean_filter(
            should_filters=[
                {
                    "query_string": {
                        "default_field": EsRecordDataFieldNames.words,
                        "default_operator": "AND",
                        "query": text_query,
                        "boost": "2.0",
                    }
                },
                {
                    "query_string": {
                        "default_field": f"{EsRecordDataFieldNames.words}.extended",
                        "default_operator": "AND",
                        "query": text_query,
                    }
                },
            ],
            minimum_should_match="50%",
        )

    @staticmethod
    def match_all():
        return {"match_all": {}}

    @staticmethod
    def ids_filter(ids: List[str]):
        return {"ids": {"values": ids}}


class aggregations:
    """Group of functions related to elasticsearch aggregations requests"""

    DEFAULT_AGGREGATION_SIZE = 1000  # TODO: Improve this logic
    MAX_AGGREGATION_SIZE = 5000  # TODO: improve by setting env var

    @staticmethod
    def nested_aggregation(nested_path: str, inner_aggregation: Dict[str, Any]):
        inner_meta = list(inner_aggregation.values())[0].get("meta", {})
        return {
            "meta": {
                "kind": inner_meta.get("kind", "custom"),
            },
            "nested": {"path": nested_path},
            "aggs": inner_aggregation,
        }

    @staticmethod
    def bidimentional_terms_aggregations(
        field_name_x: str, field_name_y: str, size=DEFAULT_AGGREGATION_SIZE
    ):
        return {
            **aggregations.terms_aggregation(field_name_x, size=size),
            "meta": {"kind": "2d-terms"},
            "aggs": {
                field_name_y: aggregations.terms_aggregation(field_name_y, size=size)
            },
        }

    @staticmethod
    def terms_aggregation(
        field_name: str = None,
        script: Union[str, Dict[str, Any]] = None,
        missing: Optional[str] = None,
        size: int = DEFAULT_AGGREGATION_SIZE,
    ):
        assert field_name or script, "Either field name or script must be provided"
        if script:
            query_part = {"script": script}
        else:
            query_part = {"field": field_name}

        dynamic_args = {}
        if missing is not None:
            dynamic_args["missing"] = missing

        return {
            "meta": {"kind": "terms"},
            "terms": {
                **query_part,
                "size": min(
                    size or aggregations.DEFAULT_AGGREGATION_SIZE,
                    aggregations.MAX_AGGREGATION_SIZE,
                ),
                "order": {"_count": "desc"},
                **dynamic_args,
            },
        }

    @staticmethod
    def histogram_aggregation(
        field_name: str = None,
        script: Union[str, Dict[str, Any]] = None,
        interval: float = 0.1,
    ):

        assert field_name or script, "Either field name or script must be provided"

        if script:
            query_part = {"script": script}
        else:
            query_part = {"field": field_name}

        return {
            "meta": {
                "kind": "histogram",
            },
            "histogram": {
                **query_part,
                "interval": interval or 0.1,
            },
        }

    @staticmethod
    def predicted_by(size: int = DEFAULT_AGGREGATION_SIZE):
        """Predicted by aggregation"""
        return {
            "predicted_by": {
                "terms": {
                    "field": decode_field_name(EsRecordDataFieldNames.predicted_by),
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
        }

    @staticmethod
    def annotated_by(size: int = DEFAULT_AGGREGATION_SIZE):
        """Annotated by aggregation"""
        return {
            "annotated_by": {
                "terms": {
                    "field": decode_field_name(EsRecordDataFieldNames.annotated_by),
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
        }

    @staticmethod
    def status(size: int = DEFAULT_AGGREGATION_SIZE):
        """Status aggregation"""
        return {
            "status": {
                "terms": {
                    "field": decode_field_name(EsRecordDataFieldNames.status),
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
        }

    @staticmethod
    def custom_fields(
        fields_definitions: Dict[str, str],
        size: int = DEFAULT_AGGREGATION_SIZE,
    ) -> Dict[str, Dict[str, Any]]:
        """Build a set of aggregations for a given field definition (extracted from index mapping)"""

        def __resolve_aggregation_for_field_type(
            field_type: str, field_name: str
        ) -> Optional[Dict[str, Any]]:
            if field_type in ["keyword", "long", "integer", "boolean"]:
                return {
                    "terms": {
                        "field": field_name,
                        "size": size or aggregations.DEFAULT_AGGREGATION_SIZE,
                        "order": {"_count": "desc"},
                    }
                }
            if field_type in ["float", "long"]:
                # TODO: Revise boxplot (since elasticsearch version 7.11 and not sure for opensearch)
                return {"extended_stats": {"field": field_name}}
            return None  # TODO: revise elasticsearch aggregations for API match

        if not fields_definitions:
            return {}

        return {
            key: aggregation
            for key, type_ in fields_definitions.items()
            for aggregation in [
                __resolve_aggregation_for_field_type(type_, field_name=key)
            ]
            if aggregation
        }

    @staticmethod
    def words_cloud(size: int = DEFAULT_AGGREGATION_SIZE):
        """Words cloud aggregation"""
        return {
            "words": {
                "terms": {
                    "field": EsRecordDataFieldNames.words,
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
        }

    @staticmethod
    def predicted_as(size: int = DEFAULT_AGGREGATION_SIZE):
        """Predicted as aggregation"""
        return {
            "predicted_as": {
                "terms": {
                    "field": decode_field_name(EsRecordDataFieldNames.predicted_as),
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
        }

    @staticmethod
    def annotated_as(size: int = DEFAULT_AGGREGATION_SIZE):
        """Annotated as aggregation"""

        return {
            "annotated_as": {
                "terms": {
                    "field": decode_field_name(EsRecordDataFieldNames.annotated_as),
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
        }

    @staticmethod
    def predicted(size: int = DEFAULT_AGGREGATION_SIZE):
        """Predicted aggregation"""
        return {
            "predicted": {
                "terms": {
                    "field": decode_field_name(EsRecordDataFieldNames.predicted),
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
        }

    @staticmethod
    def score(range_from: float = 0.0, range_to: float = 1.0, interval: float = 0.05):
        decimals = 0
        _interval = interval
        while _interval < 1:
            _interval *= 10
            decimals += 1

        ten_decimals = math.pow(10, decimals)

        int_from = math.floor(range_from * ten_decimals)
        int_to = math.floor(range_to * ten_decimals)
        int_interval = math.floor(interval * ten_decimals)

        return {
            "score": {
                "range": {
                    "field": EsRecordDataFieldNames.score,
                    "keyed": True,
                    "ranges": [
                        {"from": _from / ten_decimals, "to": _to / ten_decimals}
                        for _from, _to in zip(
                            range(int_from, int_to, int_interval),
                            range(
                                int_from + int_interval,
                                int_to + int_interval,
                                int_interval,
                            ),
                        )
                    ]
                    + [{"from": range_to}],
                }
            }
        }


def find_nested_field_path(
    field_name: str, mapping_definition: Dict[str, Any]
) -> Optional[str]:
    """
    Given a field name, find the nested path if any related to field name
    definition in provided mapping definition

    Parameters
    ----------
    field_name:
        The field name
    mapping_definition:
        A mapping definition where field name is defined

    Returns
    -------
        The found nested path if any, None otherwise
    """

    def build_flatten_properties_map(
        properties: Dict[str, Any], prefix: str = ""
    ) -> Dict[str, Any]:
        results = {}
        for prop_name, prop_value in properties.items():
            if prefix:
                prop_name = f"{prefix}.{prop_name}"
            if "type" in prop_value:
                results[prop_name] = prop_value["type"]
            if "properties" in prop_value:
                results.update(
                    build_flatten_properties_map(
                        prop_value["properties"], prefix=prop_name
                    )
                )
        return results

    properties_map = build_flatten_properties_map(mapping_definition)
    for prop in properties_map:
        if properties_map[prop] == "nested" and field_name.startswith(prop):
            return prop
    return None
