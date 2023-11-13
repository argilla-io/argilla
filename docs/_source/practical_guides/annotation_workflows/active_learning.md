# 🧑‍🏫 Active Learning

## Feedback Dataset

```{note}
The `FeedbackDataset` does not offer support for active learning as of now. If you would like to use it, you will need to use one of the other datasets. To get more info about the dataset differences, you can have a look [here](/practical_guides/choose_dataset).
```

## Other datasets

Supervised machine learning often requires large amounts of labeled data that are expensive to generate. *Active Learning* systems attempt to overcome this labeling bottleneck. The underlying idea is that not all data points are equally important for training the model. The *Active Learning* system tries to query only the most relevant data from a pool of unlabeled data to be labeled by a so-called *oracle*, which is often a human annotator. Therefore, *Active Learning* systems are usually much more sample-efficient and need far less training data than traditional supervised systems.

*Active Learning* systems can be a bit overwhelming to set up, therefore we have defined a step-by-step [tutorial](/tutorials_and_integrations/tutorials/other_datasets/few_shot_text_classification_with_active_learning.ipynb).