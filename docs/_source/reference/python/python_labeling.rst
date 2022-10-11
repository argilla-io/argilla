.. _python_labeling:

Labeling
========

The ``argilla.labeling`` module aims at providing tools to enhance your labeling workflow.


Text classification
-------------------

Labeling tools for the text classification task.

.. automodule:: argilla.labeling.text_classification.rule
   :members:
   :special-members: __call__
   :exclude-members: RuleNotAppliedError

.. automodule:: argilla.labeling.text_classification.weak_labels
   :members: WeakLabels, WeakMultiLabels

.. automodule:: argilla.labeling.text_classification.label_models
   :members: MajorityVoter, Snorkel, FlyingSquid

.. automodule:: argilla.labeling.text_classification.label_errors
   :members: find_label_errors
