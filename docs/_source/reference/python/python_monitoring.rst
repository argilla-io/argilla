.. _python_monitoring:

Monitoring
=======

Here we describe the available monitors in Argilla:

- Base Monitor: Internal mechanism to queue and log monitored predictions
- ArgillaLogHTTPMiddleware: Asgi middleware to monitor API endpoints
- Framework Monitors: Monitors to wrap around common NLP inference frameworks


Base Monitor
------------

.. automodule:: argilla.monitoring.base
   :members:

ArgillaLogHTTPMiddleware
------------------------

.. automodule:: argilla.monitoring.asgi
   :members:

Framework Monitors
------------------

.. automodule:: argilla.monitoring.model_monitor
   :members:



