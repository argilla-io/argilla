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
