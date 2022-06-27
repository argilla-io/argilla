.. _python_labeling:

Labeling
========

The ``rubrix.labeling`` module aims at providing tools to enhance your labeling workflow.


Text classification
-------------------

Labeling tools for the text classification task.

.. automodule:: rubrix.labeling.text_classification.rule
   :members:
   :special-members: __call__
   :exclude-members: RuleNotAppliedError

.. automodule:: rubrix.labeling.text_classification.weak_labels
   :members: WeakLabels, WeakMultiLabels

.. automodule:: rubrix.labeling.text_classification.label_models
   :members: MajorityVoter, Snorkel, FlyingSquid

.. automodule:: rubrix.labeling.text_classification.label_errors
   :members: find_label_errors
