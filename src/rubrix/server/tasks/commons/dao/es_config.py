from typing import Any, Dict, List

from rubrix._constants import MAX_KEYWORD_LENGTH
from rubrix.server.commons.settings import settings

EXTENDED_ANALYZER_REF = "extended_analyzer"

MULTILINGUAL_STOP_ANALYZER_REF = "multilingual_stop_analyzer"

DEFAULT_SUPPORTED_LANGUAGES = ["es", "en", "fr", "de"]  # TODO: env var configuration


class mappings:
    @staticmethod
    def keyword_field():
        """Mappings config for keyword field"""
        return {
            "type": "keyword",
            # TODO: Use environment var and align with fields validators
            "ignore_above": MAX_KEYWORD_LENGTH,
        }

    @staticmethod
    def path_match_keyword_template(path: str):
        """Dynamic template mappings config for keyword field based on path match"""
        return {
            "path_match": path,
            "match_mapping_type": "string",
            "mapping": mappings.keyword_field(),
        }

    @staticmethod
    def words_text_field():
        """Mappings config for old `word` field. Deprecated"""

        default_analyzer = settings.default_es_search_analyzer
        exact_analyzer = settings.exact_es_search_analyzer

        if default_analyzer == "standard":
            default_analyzer = MULTILINGUAL_STOP_ANALYZER_REF

        if exact_analyzer == "whitespace":
            exact_analyzer = EXTENDED_ANALYZER_REF

        return {
            "type": "text",
            "fielddata": True,
            "analyzer": default_analyzer,
            "fields": {
                "extended": {
                    "type": "text",
                    "analyzer": exact_analyzer,
                }
            },
        }

    @staticmethod
    def text_field():
        """Mappings config for textual field"""
        default_analyzer = settings.default_es_search_analyzer
        exact_analyzer = settings.exact_es_search_analyzer

        return {
            "type": "text",
            "analyzer": default_analyzer,
            "fields": {
                "exact": {"type": "text", "analyzer": exact_analyzer},
                "wordcloud": {
                    "type": "text",
                    "analyzer": MULTILINGUAL_STOP_ANALYZER_REF,
                    "fielddata": True,
                },
            },
            # TODO(@frascuchon): verify min es version that support meta fields
            # "meta": {"experimental": "true"},
        }

    @staticmethod
    def source(includes: List[str] = None, excludes: List[str] = None):
        """Source configuration with included and excluded fields"""
        source = {}
        if includes:
            source["includes"] = includes
        if excludes:
            source["excludes"] = excludes
        return source

    @staticmethod
    def nested_field():
        """Nested field mapping basic configuration"""
        return {"type": "nested", "include_in_root": True}

    @staticmethod
    def decimal_field():
        return {"type": "float"}


def multilingual_stop_analyzer(supported_langs: List[str] = None) -> Dict[str, Any]:
    """Multilingual stop analyzer"""
    from stopwordsiso import stopwords

    supported_langs = supported_langs or DEFAULT_SUPPORTED_LANGUAGES
    return {
        "type": "stop",
        "stopwords": [w for w in stopwords(supported_langs)],
    }


def extended_analyzer():
    """Extended analyzer (used only in `word` field). Deprecated"""
    return {
        "type": "custom",
        "tokenizer": "whitespace",
        "filter": ["lowercase", "asciifolding"],
    }


def tasks_common_settings():
    """Common index settings"""
    return {
        "number_of_shards": settings.es_records_index_shards,
        "number_of_replicas": settings.es_records_index_replicas,
        "analysis": {
            "analyzer": {
                MULTILINGUAL_STOP_ANALYZER_REF: multilingual_stop_analyzer(),
                EXTENDED_ANALYZER_REF: extended_analyzer(),
            }
        },
    }


def dynamic_metrics_text():
    return {"metrics.*": mappings.path_match_keyword_template(path="metrics.*")}


def dynamic_metadata_text():
    return {"metadata.*": mappings.path_match_keyword_template(path="metadata.*")}


def tasks_common_mappings():
    """Commons index mappings"""
    return {
        # TODO(@frascuchon): verify min es version that support meta fields
        # "_meta": {"version.min": "0.10"},
        "dynamic": "strict",
        "properties": {
            "id": mappings.keyword_field(),
            "words": mappings.words_text_field(),
            "text": mappings.text_field(),
            "prediction": {"type": "object", "enabled": False},
            "annotation": {"type": "object", "enabled": False},
            "status": mappings.keyword_field(),
            "event_timestamp": {"type": "date"},
            "last_updated": {"type": "date"},
            "annotated_by": mappings.keyword_field(),
            "predicted_by": mappings.keyword_field(),
            "metrics": {"dynamic": True, "type": "object"},
            "metadata": {"dynamic": True, "type": "object"},
        },
        "dynamic_templates": [
            dynamic_metadata_text(),
            dynamic_metrics_text(),
        ],
    }
