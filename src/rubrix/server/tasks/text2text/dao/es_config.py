from rubrix.server.tasks.commons.dao.es_config import mappings


def text2text_mappings():
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
            "annotated_as": mappings.text_field(),
            "predicted_as": mappings.text_field(),
            "text_predicted": mappings.words_text_field(),
            "score": {"type": "float"},
        },
    }
