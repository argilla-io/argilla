import rubrix
from rubrix.monitoring.base import BaseMonitor


def mock_monitor(monitor: BaseMonitor, monkeypatch):
    def log(*args, **kwargs):
        log_args = monitor._prepare_log_data(*args, **kwargs)
        log_args.pop("verbose", None)
        log_args.pop("background", None)
        return rubrix.log(**log_args, background=False)

    monkeypatch.setattr(monitor, "log_async", log)
