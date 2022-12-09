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

from typing import List

from argilla.server.settings import settings


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
            text_field = mappings.text_field()
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
    def text_field():
        """Mappings config for textual field"""
        default_analyzer = settings.default_es_search_analyzer
        exact_analyzer = settings.exact_es_search_analyzer

        return {
            "type": "text",
            "analyzer": default_analyzer,
            "fields": {
                "exact": {
                    "type": "text",
                    "analyzer": exact_analyzer,
                },
                # "wordcloud": {
                #     "type": "text",
                #     "analyzer": MULTILINGUAL_STOP_ANALYZER_REF,
                #     "fielddata": True,
                # },
            },
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

    @classmethod
    def dynamic_field(cls):
        return {"dynamic": True, "type": "object"}


def tasks_common_settings():
    """Common index settings"""
    return {
        "number_of_shards": settings.es_records_index_shards,
        "number_of_replicas": settings.es_records_index_replicas,
    }


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
    return {
        path: mappings.path_match_keyword_template(
            path=path, enable_text_search_in_keywords=True
        )
    }


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
            "event_timestamp": {"type": "date"},
            "last_updated": {"type": "date"},
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
