.. _python_training:

Training
========

Here we describe the available trainers in Argilla:

- :ref:`python ref base_trainer`: Internal mechanism to handle Trainers
- :ref:`python ref setfit_trainer`: Internal mechanism for handling training logic of SetFit models
- :ref:`python ref openai_trainer`: Internal mechanism for handling training logic of OpenAI models
- :ref:`python ref peft_trainer`: Internal mechanism for handling training logic of PEFT (LoRA) models
- :ref:`python ref spacy_trainer`: Internal mechanism for handling training logic of spaCy models
- :ref:`python ref transformers_trainer`: Internal mechanism for handling training logic of Transformers models
- :ref:`python ref span_marker_trainer`: Internal mechanism for handling training logic of SpanMarker models
- :ref:`python ref trl_trainer`: Internal mechanism for handling training logic of TRL models
- :ref:`python ref sentence_transformers_trainer`: Internal mechanism for handling training logic of SentenceTransformer models


.. _python ref base_trainer:

Base Trainer
------------

.. automodule:: argilla.training.base
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: FrameworkCardData

.. _python ref setfit_trainer:

SetFit Trainer
--------------

.. automodule:: argilla.training.setfit
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: SetFitModelCardData

.. _python ref openai_trainer:

OpenAI Trainer
--------------

.. automodule:: argilla.training.openai
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: OpenAIModelCardData

.. _python ref peft_trainer:

PEFT (LoRA) Trainer
-------------------

.. automodule:: argilla.training.peft
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: PeftModelCardData

.. _python ref spacy_trainer:

spaCy Trainer
-------------

.. automodule:: argilla.training.spacy
   :members: _ArgillaSpaCyTrainerBase, ArgillaSpaCyTrainer, ArgillaSpaCyTransformersTrainer

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: SpaCyModelCardData, SpacyTransformersModelCardData

.. _python ref transformers_trainer:

Transformers Trainer
--------------------

.. automodule:: argilla.training.transformers
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: TransformersModelCardData

.. _python ref span_marker_trainer:

SpanMarker Trainer
------------------

.. automodule:: argilla.training.span_marker
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: SpanMarkerModelCardData

.. _python ref trl_trainer:

TRL Trainer
------------------

.. automodule:: argilla.client.feedback.training.frameworks.trl
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: TRLModelCardData

.. _python ref sentence_transformers_trainer:

SentenceTransformer Trainer
------------------

.. automodule:: argilla.client.feedback.training.frameworks.sentence_transformers
   :members:

.. automodule:: argilla.client.feedback.integrations.huggingface.model_card
   :members: SentenceTransformerCardData

