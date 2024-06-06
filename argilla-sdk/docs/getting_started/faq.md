---
description: Argilla-python is the reference argilla python server SDK.
hide: toc
---

# FAQs

??? Question "What is Argilla?"

    Argilla is a collaboration platform for AI engineers and domain experts that require high-quality outputs, full data ownership, and overall efficiency. It is designed to help you achieve and keep high-quality data standards, store your training data, store the results of your models, evaluate their performance, and improve the data through human and AI feedback.

??? Question "Does Argilla cost money?"

    No. Argilla is an open-source project and is free to use. You can deploy Argilla on your own infrastructure or use our cloud offering.

??? Question "What data types does Argilla support?"

    Text data, mostly. Argilla natively supports textual data, however, we do support rich text, which means you can represent different types of data in Argilla as long as you can convert it to text. For example, you can store images, audio, video, and any other type of data as long as you can convert it to their base64 representation or render them as HTML in for example an IFrame.

??? Question "Does Argilla train models?"

    No. Argilla is a collaboration platform to achieve and keep high-quality data standards. You can use Argilla to store your training data, store the results of your models, evaluate their performance and improve the data. For training models, you can use any machine learning framework or library that you prefer even though we recommend starting with [Hugging Face Transformers](https://github.com/huggingface/transformers).

??? Question "Does Argilla provide annotation workforces?"

    Yes, kind of. We don't provide annotation workforce in-house but we do have partnerships with workforce providers that ensure ethical practices and secure work environments. Feel free to schedule a meeting here or contact us via email.

??? Question "How does Argilla differ from competitors like Lilac, Snorkel, Prodigy and Scale?"

    Argilla distinguishes itself for its focus on specific use cases and human-in-the-loop approaches. While it does offer programmatic features, Argilla’s core value lies in actively involving human experts in the tool-building process, setting it apart from other competitors.

    Furthermore, Argilla places particular emphasis on smooth integration with other tools in the community, particularly within the realms of MLOps and NLP. So, its compatibility with popular frameworks like spaCy and Hugging Face makes it exceptionally user-friendly and accessible.

    Finally, platforms like Snorkel, Prodigy or Scale, while more comprehensive, often require a significant commitment. Argilla, on the other hand, works more as a component within the MLOps ecosystem, allowing users to begin with specific use cases and then scale up as needed. This flexibility is particularly beneficial for users and customers who prefer to start small and expand their applications over time, as opposed to committing to an all-encompassing platform from the outset.

??? Question "What is the difference between Argilla 2.0 and the legacy datasets in 1.0?"

    Argilla 1.0 relied on 3 main task datasets: `DatasetForTextClassification`, `DatasetForTokenClassification`, and `DatasetForText2Text`. These tasks were designed to be simple, easy to use and high in functionality but they were limited in adaptability. With the introduction of Large Language Models (LLMs) and the increasing complexity of NLP tasks, we realized that we needed to expand the capabilities of Argilla to support more advanced feedback mechanisms which led to the introduction of the `FeedbackDataset`. Compared to its predecessor it was high in adaptability but still limited in functionality. After having ported all of the functionality of the legacy tasks to the new `FeedbackDataset`, we decided to deprecate the legacy tasks in favor of a brand new SDK with the `FeedbackDataset` at its core.