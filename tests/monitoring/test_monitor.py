import warnings

import rubrix


class MockModel:
    pass


def test_monitor_with_non_supported_model():
    with warnings.catch_warnings(record=True) as warning_list:
        model = MockModel()

        maybe_monitored = rubrix.monitor(model, dataset="mock")
        assert model == maybe_monitored
        assert len(warning_list) == 1
        warn_text = warning_list[0].message.args[0]
        assert (
            warn_text
            == "The provided task model is not supported by monitoring module. "
            "Predictions won't be logged into rubrix"
        )


def test_monitor_non_supported_huggingface_model():
    with warnings.catch_warnings(record=True) as warning_list:

        from transformers import AutoTokenizer, AutoModelForTokenClassification
        from transformers import pipeline

        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

        nlp = pipeline("ner", model=model, tokenizer=tokenizer)
        maybe_monitored = rubrix.monitor(nlp, dataset="ds")
        assert nlp == maybe_monitored
        assert len(warning_list) == 1
        warn_text = warning_list[0].message.args[0]
        assert (
                warn_text
                == "The provided task model is not supported by monitoring module. "
                   "Predictions won't be logged into rubrix"
        )
