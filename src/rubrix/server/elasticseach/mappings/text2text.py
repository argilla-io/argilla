from rubrix.server.elasticseach.mappings.helpers import mappings


def text2text_mappings():
    """Text2Text index mappings"""
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
            "annotated_as": mappings.keyword_field(),
            "predicted_as": mappings.keyword_field(),
            "text_predicted": mappings.words_text_field(),
            "score": {"type": "float"},
        },
    }
