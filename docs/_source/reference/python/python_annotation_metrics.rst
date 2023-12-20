.. _python_annotation_metrics:

Annotation metrics
==================

Here we describe the available metrics in Argilla:

- :ref:`python ref agreement_metrics`: Metrics of agreement on an annotation task
- :ref:`python ref annotator_metrics`: Metrics for annotators. Includes both metrics per annotator and unified metrics
  for all annotators.

.. _python ref metrics:

Base Metric
-----------

.. automodule:: argilla.client.feedback.metrics.base
   :members: AgreementMetricResult, ModelMetricResult

.. autoclass:: argilla.client.feedback.metrics.base.MetricBase
   :members: __init__, compute, allowed_metrics

.. _python ref agreement_metrics:

Agreement Metrics
-----------------

.. automodule:: argilla.client.feedback.metrics.agreement_metrics
   :members:
   :exclude-members: kendall_tau_dist, prepare_dataset_for_annotation_task, AgreementMetric

.. autoclass:: argilla.client.feedback.metrics.agreement_metrics.AgreementMetric
   :members: __init__, compute

.. _python ref annotator_metrics:

Annotator Metrics
-----------------

.. automodule:: argilla.client.feedback.metrics.annotator_metrics
   :members:


.. autoclass:: argilla.client.feedback.metrics.annotator_metrics.ModelMetric
   :members: __init__, compute

.. autoclass:: argilla.client.feedback.metrics.annotator_metrics.UnifiedModelMetric
   :members: __init__, compute
