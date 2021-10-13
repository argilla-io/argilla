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
from typing import Any, Dict, List, Optional, Union

from stopwordsiso import stopwords

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.commons.es_settings import DATASETS_RECORDS_INDEX_NAME
from rubrix.server.commons.settings import settings
from rubrix.server.tasks.commons import (
    PredictionStatus,
    ScoreRange,
    SortableField,
    TaskStatus,
)
from rubrix.server.tasks.commons.api import EsRecordDataFieldNames

SUPPORTED_LANGUAGES = ["es", "en", "fr", "de"]
DATASETS_RECORDS_INDEX_TEMPLATE = {
    "settings": {
        "number_of_shards": settings.es_records_index_shards,
        "number_of_replicas": settings.es_records_index_replicas,
        "analysis": {
            "analyzer": {
                "multilingual_stop_analyzer": {
                    "type": "stop",
                    "stopwords": [w for w in stopwords(SUPPORTED_LANGUAGES)],
                },
                "extended_analyzer": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": ["lowercase", "asciifolding"],
                },
            }
        },
    },
    "index_patterns": [DATASETS_RECORDS_INDEX_NAME.format("*")],
    "mappings": {
        "properties": {
            EsRecordDataFieldNames.event_timestamp: {"type": "date"},
            # TODO(in new index version): Data based on text field with multiple fields:
            #   - keywords: for words aggregations
            #   - extended: including stop words and special characters in search
            EsRecordDataFieldNames.words: {
                "type": "text",
                "fielddata": True,
                "analyzer": "multilingual_stop_analyzer",
                "fields": {
                    "extended": {"type": "text", "analyzer": "extended_analyzer"}
                },
            },
            EsRecordDataFieldNames.predicted_as: {
                "type": "keyword",
                "ignore_above": MAX_KEYWORD_LENGTH,
            },
            EsRecordDataFieldNames.predicted_by: {
                "type": "keyword",
                "ignore_above": MAX_KEYWORD_LENGTH,
            },
            EsRecordDataFieldNames.annotated_as: {
                "type": "keyword",
                "ignore_above": MAX_KEYWORD_LENGTH,
            },
            EsRecordDataFieldNames.annotated_by: {
                "type": "keyword",
                "ignore_above": MAX_KEYWORD_LENGTH,
            },
            EsRecordDataFieldNames.status: {
                "type": "keyword",
            },
            EsRecordDataFieldNames.predicted: {
                "type": "keyword",
            },
        },
        "dynamic_templates": [
            {
                "metadata_strings": {
                    "path_match": "metadata.*",
                    "match_mapping_type": "string",
                    "mapping": {
                        "type": "keyword",
                        "ignore_above": MAX_KEYWORD_LENGTH,
                    },
                }
            },
        ],
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
                f"Wrong sort id {sortable_field.id}. Valid values are"
                f"[{valid_fields}]"
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
            key, doc_count, meta, _from, _to = (
                bucket.pop("key", None),
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
            elif key:
                parsed.update({key: doc_count})
        return parsed

    result = {}
    for key, values in es_aggregations.items() or {}:
        if "buckets" in values:
            result[key] = parse_buckets(values["buckets"])
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
    def predicted_as(predicted_as: List[str] = None) -> Optional[Dict[str, Any]]:
        """Filter records with given predicted as terms"""
        if not predicted_as:
            return None
        return {
            "terms": {
                decode_field_name(EsRecordDataFieldNames.predicted_as): predicted_as
            }
        }

    @staticmethod
    def annotated_as(annotated_as: List[str] = None) -> Optional[Dict[str, Any]]:
        """Filter records with given predicted as terms"""

        if not annotated_as:
            return None
        return {
            "terms": {
                decode_field_name(EsRecordDataFieldNames.annotated_as): annotated_as
            }
        }

    @staticmethod
    def predicted(predicted: PredictionStatus = None) -> Optional[Dict[str, Any]]:
        """Filter records with given predicted status"""
        if predicted is None:
            return None
        return {
            "term": {decode_field_name(EsRecordDataFieldNames.predicted): predicted}
        }

    @staticmethod
    def text_query(text_query: Optional[str]) -> Dict[str, Any]:
        """Filter records matching text query"""
        if text_query is None:
            return {"match_all": {}}
        return {
            "bool": {
                "should": [
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
                "minimum_should_match": "50%",
            }
        }

    @staticmethod
    def score(
        score: Optional[ScoreRange],
    ) -> Optional[Dict[str, Any]]:
        if score is None:
            return None

        score_filter = {}
        if score.range_from is not None:
            score_filter["gte"] = score.range_from
        if score.range_to is not None:
            score_filter["lte"] = score.range_to

        return {"range": {EsRecordDataFieldNames.score: score_filter}}


class aggregations:
    """Group of functions related to elasticsearch aggregations requests"""

    DEFAULT_AGGREGATION_SIZE = 100

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
    def terms_aggregation(field_name: str, size: int = DEFAULT_AGGREGATION_SIZE):
        return {
            "meta": {"kind": "terms"},
            "terms": {
                "field": field_name,
                "size": size,
                "order": {"_count": "desc"},
            },
        }

    @staticmethod
    def histogram_aggregation(field_name: str, interval: float = 0.1):
        return {
            "meta": {
                "kind": "histogram",
            },
            "histogram": {
                "field": field_name,
                "interval": interval,
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
            if field_type in ["keyword", "long", "integer"]:
                return {
                    "terms": {
                        "field": field_name,
                        "size": size,
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
