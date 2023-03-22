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

from typing import Any, Dict, List

from argilla.server.daos.backend.mappings.stopwords import english
from argilla.server.settings import settings

MULTILINGUAL_STOP_ANALYZER_REF = "multilingual_stop_analyzer"


class mappings:
    @staticmethod
    def keyword_field(
        enable_text_search: bool = False,
    ):
        """Mappings config for keyword field"""
        mapping = {
            "type": "keyword",
        }
        if enable_text_search:
            text_field = mappings.text_field(with_wordcloud=False)
            text_field_fields = text_field.pop("fields", {})
            mapping["fields"] = {"text": text_field, **text_field_fields}
        return mapping

    @staticmethod
    def path_match_keyword_template(
        path: str,
        enable_text_search_in_keywords: bool = False,
    ):
        """Dynamic template mappings config for keyword field based on path match"""
        return {
            "path_match": path,
            "match_mapping_type": "string",
            "mapping": mappings.keyword_field(
                enable_text_search=enable_text_search_in_keywords,
            ),
        }

    @staticmethod
    def text_field(with_wordcloud: bool = True):
        """Mappings config for textual field"""
        default_analyzer = settings.default_es_search_analyzer
        exact_analyzer = settings.exact_es_search_analyzer

        mappings = {
            "type": "text",
            "analyzer": default_analyzer,
            "fields": {
                "exact": {
                    "type": "text",
                    "analyzer": exact_analyzer,
                },
            },
        }

        if with_wordcloud:
            mappings["fields"]["wordcloud"] = {
                "type": "text",
                "fielddata": True,
                "fielddata_frequency_filter": {
                    "min": 0.001,
                    "max": 0.1,
                    "min_segment_size": 500,
                },
                "analyzer": MULTILINGUAL_STOP_ANALYZER_REF,
            }

        return mappings

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

    @staticmethod
    def non_searchable_text_field():
        return {"type": "text", "index": False}

    @classmethod
    def dynamic_field(cls):
        return {"dynamic": True, "type": "object"}


def configure_multilingual_stop_analyzer(
    settings: Dict[str, Any],
    supported_langs: List[str] = None,
):
    lang2elastic_stop = {
        "en": english.STOPWORDS,
        "es": "_spanish_",
        "fr": "_french_",
        "de": "_german_",
    }

    supported_langs = supported_langs or [lang for lang in lang2elastic_stop]

    def get_value_with_defaults(data: dict, key: str, default):
        prop = data.get(key)
        if prop is None:
            data[key] = default
        return data[key]

    analysis = get_value_with_defaults(settings, "analysis", {})
    filter = get_value_with_defaults(analysis, "filter", {})
    analyzer = get_value_with_defaults(analysis, "analyzer", {})

    filters = []
    for lang in supported_langs:
        stopwords = lang2elastic_stop.get(lang)
        if stopwords:
            filter[lang] = {
                "type": "stop",
                "stopwords": stopwords,
            }
            filters.append(lang)

    analyzer[MULTILINGUAL_STOP_ANALYZER_REF] = {
        "tokenizer": "lowercase",
        "filter": filters,
    }

    return settings


def extended_analyzer():
    """Extended analyzer (used only in `word` field). Deprecated"""
    return {
        "type": "custom",
        "tokenizer": "whitespace",
        "filter": ["lowercase", "asciifolding"],
    }


def tasks_common_settings():
    """Common index settings"""
    es_settings = {
        "number_of_shards": settings.es_records_index_shards,
        "number_of_replicas": settings.es_records_index_replicas,
    }

    configure_multilingual_stop_analyzer(settings=es_settings)
    return es_settings


def dynamic_metrics_text():
    return {
        "metrics.*": mappings.path_match_keyword_template(
            path="metrics.*",
            enable_text_search_in_keywords=False,
        )
    }


def dynamic_metadata_text():
    return {
        "metadata.*": mappings.path_match_keyword_template(
            path="metadata.*",
            enable_text_search_in_keywords=True,
        )
    }


def dynamic_annotations_text(path: str):
    path = f"{path}.*"
    return {path: mappings.path_match_keyword_template(path=path, enable_text_search_in_keywords=True)}


def tasks_common_mappings():
    """Commons index mappings"""
    return {
        # TODO(@frascuchon): verify min es version that support meta fields
        # "_meta": {"version.min": "0.10"},
        "dynamic": "strict",
        "properties": {
            "id": mappings.keyword_field(),
            "text": mappings.text_field(),
            # TODO(@frascuchon): Enable prediction and annotation
            #  so we can build extra metrics based on these fields
            "prediction": {"type": "object", "enabled": False},
            "annotation": {"type": "object", "enabled": False},
            "predictions": mappings.dynamic_field(),
            "annotations": mappings.dynamic_field(),
            "status": mappings.keyword_field(),
            "event_timestamp": {"type": "date_nanos"},
            "last_updated": {"type": "date_nanos"},
            "annotated_by": mappings.keyword_field(enable_text_search=True),
            "predicted_by": mappings.keyword_field(enable_text_search=True),
            "metrics": mappings.dynamic_field(),
            "metadata": mappings.dynamic_field(),
            "vectors": mappings.dynamic_field(),
        },
        "dynamic_templates": [
            dynamic_metadata_text(),
            dynamic_metrics_text(),
            dynamic_annotations_text(path="predictions"),
            dynamic_annotations_text(path="annotations"),
        ],
    }
