from rubrix import *

from rubrix.sdk import models as sdk_models


def test_model_2_sdk_model():

    record = TextClassificationRecord(
        inputs={"text": "data text"},
        annotation=TextClassificationAnnotation(
            agent="test", labels=[ClassPrediction(class_label="A", confidence=1.0)]
        ),
    )

    sdk_model = sdk_models.TextClassificationRecord.from_dict(record.asdict())
    assert record.inputs == sdk_model.inputs.to_dict()
    assert record.annotation.agent == sdk_model.annotation.agent
    assert [
        {"class": label.class_label, "confidence": label.confidence}
        for label in record.annotation.labels
    ] == [
        {"class": label.class_, "confidence": label.confidence}
        for label in sdk_model.annotation.labels
    ]
