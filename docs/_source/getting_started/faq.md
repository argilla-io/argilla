# ❔ FAQ

* *What is Argilla?*

Argilla is an open-source data curation platform for LLMs. Using Argilla, everyone can build robust language models through faster data curation using both human and machine feedback. We provide support for each step in the MLOps cycle, from data labeling to model monitoring. In fact, the inspiration behind the name "Argilla" comes from the word for "clay", in Latin, Italian and even in Catalan. And just as clay has been a fundamental medium for human creativity and tool-making throughout history, we view data as the essential material for sculpting and refining models.


* *Does Argilla train models?*

Argilla is a data curation platform that offers tools to help you train models. With Argilla, you can easily load data and train models straightforward using a feature we call the `ArgillaTrainer`. The `ArgillaTrainer` acts as a bridge to various popular NLP libraries. It simplifies the training process by offering an easy-to-understand interface for many NLP tasks using default pre-set settings without the need of converting data from Argilla's format. You can find more information about training models with Argilla [here](/practical_guides/fine_tune).


* *What is the difference between old datasets and the FeedbackDataset?*

The FeedbackDataset stands out for its versatility and adaptability, designed to support a wider range of NLP tasks including those centered on large language models. In contrast, older datasets, while more feature-rich in specific areas, are tailored to singular NLP tasks. For a more detailed explanation, please refer to [this](/practical_guides/choose_dataset) guide.


* *Can Argilla only be used for LLMs?*

No, Argilla is a versatile tool suitable for a wide range of NLP tasks. However, we emphasize the integration with large language models (LLMs), reflecting confidence in the significant role that LLMs will play in the future of NLP. In this page, you can find a list of [supported tasks](/practical_guides/choose_dataset.md#table-comparison).


* *Does Argilla provide annotation workforces?*

Currently, we do not offer this service. However, we plan on creating partnerships with annotation providers that ensure ethical practices and secure work environments.


* *Does Argilla cost money?*

No, Argilla is an open-source platform. And we plan to keep Argilla free forever. However, we do offer a commercial version of Argilla called Argilla Cloud.


* *What is the difference between Argilla open source and Argilla Cloud?*

Argilla Cloud is the counterpart to our open-source platform, offering a Software as a Service (SaaS) model, and doesn't add extra features beyond what is available in the open-source version. The main difference is its cloud-hosting, which caters especially to large teams requiring features that aren't typically necessary for individual practitioners or small businesses. So, Argilla Cloud is a SAS plus virtual private cloud deployment, with added features specifically related to the cloud. For those interested in the different plans available under Argilla Cloud, you can find detailed information on our [website](https://argilla.io/pricing).


* *How does Argilla differ from competitors like Snorkel, Prodigy and Scale?*

Argilla distinguishes itself for its focus on specific use cases and human-in-the-loop approaches. While it does offer programmatic features, Argilla's core value lies in actively involving human experts in the tool-building process, setting it apart from other competitors.

Furthermore, Argilla places particular emphasis on smooth integration with other tools in the community, particularly within the realms of MLOps and NLP. So, its compatibility with popular frameworks like SpaCy and Hugging Face makes it exceptionally user-friendly and accessible.

Finally, platforms like Snorkel, Prodigy or Scale, while more comprehensive, often require a significant commitment. Argilla, on the other hand, works more as a component within the MLOps ecosystem, allowing users to begin with specific use cases and then scale up as needed. This flexibility is particularly beneficial for users and customers who prefer to start small and expand their applications over time, as opposed to committing to an all-encompassing platform from the outset.


* *What is Argilla working on?*

We are continuously working on improving Argilla's features and usability. You can find a list of our current projects [here](https://github.com/orgs/argilla-io/projects/10/views/1)

