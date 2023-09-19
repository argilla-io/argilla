.. _python_monitoring:

Monitoring
=======

Here we describe the available monitors in Argilla:

- :ref:`python ref base_monitor`: Internal mechanism to queue and log monitored predictions
- :ref:`python ref argilla_log_http_middleware`: Asgi middleware to monitor API endpoints
- :ref:`python ref framework_monitors`:  Monitors to wrap around common NLP inference frameworks

.. _python ref base_monitor:

Base Monitor
------------

.. automodule:: argilla.monitoring.base
   :members:

.. _python ref argilla_log_http_middleware:

ArgillaLogHTTPMiddleware
------------------------

.. automodule:: argilla.monitoring.asgi
   :members:

.. _python ref framework_monitors:

Framework Monitors
------------------

.. automodule:: argilla.monitoring.model_monitor
   :members:

Transformers Monitor
^^^^^^^^^^^^^^^^^^^^

.. automodule:: argilla.monitoring._transformers
   :members:

spaCy Monitor
^^^^^^^^^^^^^

.. automodule:: argilla.monitoring._spacy
   :members:

Flair Monitor
^^^^^^^^^^^^^

.. automodule:: argilla.monitoring._flair
   :members: