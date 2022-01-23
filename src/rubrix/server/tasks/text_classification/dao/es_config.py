from rubrix.server.tasks.commons.dao.es_config import mappings


def text_classification_mappings():
    """Text classification index mappings"""
    return {
        "_source": mappings.source(
            excludes=[
                # "words", # Cannot be exclude since comment text_length metric  is computed using this source fields
                "predicted",
                "predicted_as",
                "predicted_by",
                "annotated_as",
                "annotated_by",
                "score",
            ]
        ),
        "properties": {
            "predicted": mappings.keyword_field(),
            "multi_label": {"type": "boolean"},
            "annotated_as": mappings.keyword_field(),
            "predicted_as": mappings.keyword_field(),
            "score": {"type": "float"},
        },
        "dynamic_templates": [
            {"inputs.*": {"path_match": "inputs.*", "mapping": mappings.text_field()}}
        ],
    }
