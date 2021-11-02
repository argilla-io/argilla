from rubrix.monitoring.base import BaseMonitor


def mock_monitor(monitor: BaseMonitor, monkeypatch):
    monkeypatch.setattr(monitor, "log_async", monitor._log2rubrix)
