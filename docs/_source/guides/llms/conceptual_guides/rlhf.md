# Data collection for LLMs: the ChatGPT path
The following figure shows the stages for training and fine-tuning LLMs. From top to bottom, it shows, the data needed at each stage (note the color for the data collected with human feedback), the stage (namely, pre-training, supervised fine-tuning, reward modelling, and reinforcement learning), and finally the model created at each stage. Argilla Feedback makes the process of collecting human feedback seamless at each step after pre-training.

![llm-flow](../../../_static/images/llms/rlhf.svg "LLM fine-tuning stages")

:::{note}
This guide are highly inspired by the "Training language models to follow instructions with human feedback" paper and the amazing introduction to RLHF by Chip Huyen. The above figure is an adaptation from Chip Huyen's post.
:::

Argilla Feedback assists in three critical stages of the LLM fine-tuning process. The first is the **collection of demonstration data for supervised fine-tuning of large language models**. This stage, while a part of the RLHF process, also operates independently. In supervised fine-tuning, models learn from human-guided examples, steering them, and improving their capabilities.

The second stage where Argilla Feedback proves beneficial is in the **collection of comparison data**, a key element for training a reward model for RLHF.

Similarly, Argilla Feedback can be used to write or select prompts for the last stage: Reinforcement learning. This collection process is highly similar to the first stage except that we don't ask users to write demonstrations.

To understand how Argilla Feedback works, let’s deep-dive into the **Collecting demonstration data** and **Collecting comparison data** stages.