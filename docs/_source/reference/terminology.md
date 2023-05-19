(terminology)=
# Terminology

Within Argilla we decided to differentiate our docs using main terminology classes and corresponding sub-classes.

## Features

Specific features that are covered by internal `Argilla` functionalities.
| Terminology | Description |
| :--- | :--- |
| Datasets       | Internal `Dataset` classes are lightweight containers for Argilla records.        |
| Metrics       | Argilla `Metrics` enables you to perform fine-grained analysis of your models and training datasets.        |
| Queries       | Argilla query functionalities are based on the powerful `Elasticsearch` query string syntax.        |
| Semantic Search | This built-in search uses vectors for text and enables Approximate KNN for semantic search on these vectors.    |

## MLOps Steps
All steps that we directly or in-directly cover within the `MLOps lifecycle`.

| Terminology | Description |
| :--- | :--- |
| 🏷 Labelling       | `manual or automatic` data collection and label assignment.        |
| 💪🏽 Training      |  `training and evaluation` of NLP models  |
| 👨🏽‍💻 Deploying       | `logging inference/prediction` of your ML models during their deployment.        |
| 📊 Monitoring       | `Dashboarding and evaluation` of model performance.        |


## NLP Tasks

Main task categories that we cover within the `NLP landscape`.

| Terminology | Description                                                                                                                                                              |
| :--- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 📕📗 TextClassification      | Assigning predefined category labels to `texts`. This contains sub-tasks like detecting sentiment, semantic similarity, and multi-label classification.                   |
| 🈴🈯️ TokenClassification      | Assigning predefined category labels to `words and phrases within texts` . This contains sub-tasks like Named Entity Recognition (NER) and Part-Of-Speech Tagging (POS). |
| 👨🏽💬 Text2Text       | Generating a `text` based on an input `text`.  This contains sub-tasks like machine translation, and paraphrase generation.                                              |

## Techniques

Best practices and methods that can be applied during `Machine Learning` within our eco-system.

| Terminology | Description |
| :--- | :--- |
| 🍼 Basics       | Simple `straightforward basics` for the one's just getting started.      |
| 👨🏽‍🏫 Active Learning       | Actively evaluate `prediction certainties` to determine labels that need to be evaluated for training.        |
| 👮 Weak Supervision      | Use `rules and functions` to obtain initial annotations before manually correcting them.      |
| 🔎 Explainability and bias       | `understand` and explain how a model produced a prediction and be aware of potential `systematic errors`.     |
| 🔫 Few-shot classification      | Model and techniques that perform reasonably well using only a `few or zero training samples`.        |
| 🪞 Semantic Search | This built-in search uses vectors for text and enables Approximate KNN for semantic search on these vectors.    |
