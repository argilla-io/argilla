.. _python_labeling:

Labeling (Experimental)
=======================

The ``rubrix.labeling`` module aims at providing tools to enhance your labeling workflow.


Text classification
-------------------

Labeling tools for the text classification task.

.. automodule:: rubrix.labeling.text_classification.rule
   :members:
   :special-members: __call__
   :exclude-members: RuleNotAppliedError

.. automodule:: rubrix.labeling.text_classification.weak_labels
   :members:
   :exclude-members: WeakLabelsError, DuplicatedRuleNameError, NoRecordsFoundError, MultiLabelError, MissingLabelError

.. automodule:: rubrix.labeling.text_classification.label_models
   :members:
   :exclude-members: TieBreakPolicy, LabelModelError, MissingAnnotationError, TooFewRulesError, NotFittedError

.. automodule:: rubrix.labeling.text_classification.label_errors
   :members:
   :exclude-members: SortBy, LabelErrorsException, NoRecordsError, MissingPredictionError
