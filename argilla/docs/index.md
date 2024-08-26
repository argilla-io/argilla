---
description: Argilla is a collaboration tool for AI engineers and domain experts to build high-quality datasets.
hide: navigation
---

# Welcome to Argilla

Argilla is a **collaboration tool for AI engineers and domain experts** to build high-quality datasets.

To get started:

<div class="grid cards" markdown>

-  __Get started in 5 minutes!__

    ---

    Deploy Argilla for free on the Hugging Face Hub or with `Docker`. Install the Python SDK with `pip` and create your first project.

    [:octicons-arrow-right-24: Quickstart](getting_started/quickstart.md)

-  __How-to guides__

    ---

    Get familiar with the basic workflows of Argilla. Learn how to manage `Users`, `Workspaces`, `Datasets`, and `Records` to set up your data annotation projects.

    [:octicons-arrow-right-24: Learn more](how_to_guides/index.md)

</div>

Or, play with the Argilla UI by signing in with your Hugging Face account:

<div class="iframe-wrapper">
<iframe
	src="https://argilla-argilla-template-space.hf.space"
	frameborder="0"
	width="100%"
	height="650"
></iframe>
</div>


!!! INFO "Looking for Argilla 1.x?"
    Looking for documentation for Argilla 1.x? Visit [the latest release](https://docs.v1.argilla.io/en/latest/).

!!! NOTE "Migrate to Argilla 2.x"
    Want to learn how to migrate from Argilla 1.x to 2.x? Take a look at our dedicated [Migration Guide](how_to_guides/migrate_from_legacy_datasets.md).

<!-- ## Changelog -->

## Why use Argilla?

Argilla can be used for collecting human feedback for a wide variety of AI projects like traditional NLP (text classification, NER, etc.), LLMs (RAG, preference tuning, etc.), or multimodal models (text to image, etc.).

Argilla's programmatic approach lets you build workflows for continuous evaluation and model improvement. The goal of Argilla is to ensure **your data work pays off by quickly iterating on the right data and models**.

<p style="font-size:20px">Improve your AI output quality through data quality</p>

Compute is expensive and output quality is important. We help you focus on data, which tackles the root cause of both of these problems at once. Argilla helps you to **achieve and keep high-quality standards** for your data. This means you can improve the quality of your AI outputs.

<p style="font-size:20px">Take control of your data and models</p>

Most AI tools are black boxes. Argilla is different. We believe that you should be the owner of both your data and your models. That's why we provide you with all the tools your team needs to **manage your data and models in a way that suits you best**.

<p style="font-size:20px">Improve efficiency by quickly iterating on the right data and models</p>

Gathering data is a time-consuming process. Argilla helps by providing a tool that allows you to **interact with your data in a more engaging way**. This means you can quickly and easily label your data with filters, AI feedback suggestions and semantic search. So you can focus on training your models and monitoring their performance.


## What do people build with Argilla?

<p style="font-size:20px">Datasets and models</p>

Argilla is a tool that can be used to achieve and keep **high-quality data standards** with a **focus on NLP and LLMs**. The community uses Argilla to create amazing open-source [datasets](https://huggingface.co/datasets?other=argilla) and [models](https://huggingface.co/models?other=distilabel), and **we love contributions to open-source** too.

- [cleaned UltraFeedback dataset](https://huggingface.co/datasets/argilla/ultrafeedback-binarized-preferences-cleaned) and the [Notus](https://huggingface.co/argilla/notus-7b-v1) and [Notux](https://huggingface.co/argilla/notux-8x7b-v1) models, where we improved benchmark and empirical human judgment for the Mistral and Mixtral models with cleaner data using **human feedback**.
- [distilabeled Intel Orca DPO dataset](https://huggingface.co/datasets/argilla/distilabel-intel-orca-dpo-pairs) and the [improved OpenHermes model](https://huggingface.co/argilla/distilabeled-OpenHermes-2.5-Mistral-7B), show how we improve model performance by filtering out 50% of the original dataset through **human and AI feedback**.

<p style="font-size:20px">Projects and pipelines</p>

AI teams from companies like [the Red Cross](https://510.global/), [Loris.ai](https://loris.ai/) and [Prolific](https://www.prolific.com/) use Argilla to **improve the quality and efficiency of AI** projects. They shared their experiences in the [AI community meetup](https://lu.ma/embed-checkout/evt-IQtRiSuXZCIW6FB).

- AI for good: [the Red Cross presentation](https://youtu.be/ZsCqrAhzkFU?feature=shared) showcases **how their experts and AI team collaborate** by classifying and redirecting requests from refugees of the Ukrainian crisis to streamline the support processes of the Red Cross.
- Customer support: during [the Loris meetup](https://youtu.be/jWrtgf2w4VU?feature=shared) they showed how their AI team uses unsupervised and few-shot contrastive learning to help them **quickly validate and gain labelled samples for a huge amount of multi-label classifiers**.
- Research studies: [the showcase from Prolific](https://youtu.be/ePDlhIxnuAs?feature=shared) announced their integration with Argilla. They use it to actively **distribute data collection projects** among their annotating workforce. This allows them to quickly and **efficiently collect high-quality data** for their research studies.
