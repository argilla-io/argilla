import math
from typing import Any, Dict, List, Optional, Union

from rubrix.server.commons.settings import settings
from rubrix.server.datasets.dao import (
    DATASETS_RECORDS_INDEX_NAME,
)
from rubrix.server.tasks.commons import (
    PredictionStatus,
    ScoreRange,
    TaskStatus,
)
from rubrix._constants import MAX_KEYWORD_LENGTH
from stopwordsiso import stopwords

from .api import EsRecordDataFieldNames

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
                }
            }
        },
    },
    "index_patterns": [DATASETS_RECORDS_INDEX_NAME.format("*")],
    "mappings": {
        "properties": {
            "event_timestamp": {"type": "date"},
            EsRecordDataFieldNames.words: {
                "type": "text",
                "fielddata": True,
                "analyzer": "multilingual_stop_analyzer",
            },
            # TODO: Not here since is task dependant
            "tokens": {"type": "text"},
        },
        "dynamic_templates": [
            # TODO: Not here since is task dependant
            {"inputs": {"path_match": "inputs.*", "mapping": {"type": "text"}}},
            {
                "status": {
                    "path_match": "*.status",
                    "mapping": {
                        "type": "keyword",
                    },
                }
            },
            {
                "predicted": {
                    "path_match": "*.predicted",
                    "mapping": {
                        "type": "keyword",
                    },
                }
            },
            {
                "strings": {
                    "match_mapping_type": "string",
                    "mapping": {
                        "type": "keyword",
                        "ignore_above": MAX_KEYWORD_LENGTH,  # Avoid bulk errors with too long keywords
                        # Some elasticsearch versions includes automatically raw fields, so
                        # we must limit those fields too
                        "fields": {
                            "raw": {
                                "type": "keyword",
                                "ignore_above": MAX_KEYWORD_LENGTH,
                            }
                        },
                    },
                }
            },
        ],
    },
}


def parse_aggregations(
    es_aggregations: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """Transforms elasticsearch raw aggregations into a more friendly structure"""

    if es_aggregations is None:
        return None

    def parse_buckets(buckets: List[Dict[str, Any]]) -> Dict[str, Any]:
        parsed = {}
        for bucket in buckets:
            key, doc_count = bucket.pop("key"), bucket.pop("doc_count")
            if len(bucket) == 1 and not ("from" in bucket or "to" in bucket):
                k = [k for k in bucket if k not in ["key", "doc_count"]][0]
                parsed.update({key: parse_buckets(bucket[k].get("buckets", []))})
            else:
                parsed.update({key: doc_count})

        return parsed

    return {
        key: parse_buckets(values.get("buckets", []))
        for key, values in es_aggregations.items() or {}
    }


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
    def text_query(text_query: Optional[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """Filter records matching text query"""
        if text_query is None:
            return {"match_all": {}}

        if isinstance(text_query, str):
            return {
                "query_string": {
                    "default_field": "words",
                    "default_operator": "AND",
                    "query": text_query,
                }
            }

        return {
            "bool": {
                "should": [
                    {
                        "query_string": {
                            "default_field": f"inputs.{key}",
                            "default_operator": "AND",
                            "query": query_text,
                        }
                    }
                    for key, query_text in text_query.items()
                ],
                "minimum_should_match": "100%",
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
    def bidimentional_terms_aggregations(
        name: str, field_name_x: str, field_name_y: str, size=DEFAULT_AGGREGATION_SIZE
    ):
        return {
            name: {
                "terms": {
                    "field": field_name_x,
                    "size": size,
                    "order": {"_count": "desc"},
                },
                "aggs": {
                    field_name_y: {
                        "terms": {
                            "field": field_name_y,
                            "size": size,
                            "order": {"_count": "desc"},
                        }
                    }
                },
            }
        }

    @staticmethod
    def terms_aggregation(field_name: str, size: int = DEFAULT_AGGREGATION_SIZE):
        return {
            field_name: {
                "terms": {
                    "field": field_name,
                    "size": size,
                    "order": {"_count": "desc"},
                }
            }
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
