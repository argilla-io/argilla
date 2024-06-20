<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  Argilla
  <br>
</h1>
<h3 align="center">Work on data together, make your model outputs better!</h2>

<p align="center">
<a  href="https://pypi.org/project/argilla/">
<img alt="CI" src="https://img.shields.io/pypi/v/argilla.svg?style=flat-round&logo=pypi&logoColor=white">
</a>
<img alt="Codecov" src="https://codecov.io/gh/argilla-io/argilla/branch/main/graph/badge.svg?token=VDVR29VOMG"/>
<a href="https://pepy.tech/project/argilla">
<img alt="CI" src="https://static.pepy.tech/personalized-badge/argilla?period=month&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads/month">
</a>
<a href="https://huggingface.co/new-space?template=argilla/argilla-template-space">
<img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-sm.svg"/>
</a>
</p>

<p align="center">
<a href="https://twitter.com/argilla_io">
<img src="https://img.shields.io/badge/twitter-black?logo=x"/>
</a>
<a href="https://www.linkedin.com/company/argilla-io">
<img src="https://img.shields.io/badge/linkedin-blue?logo=linkedin"/>
</a>
<a href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g">
<img src="https://img.shields.io/badge/slack-purple?logo=slack"/>
</a>
</p>

Argilla is a **collaboration platform for AI engineers and domain experts** that require **high-quality outputs, full data ownership, and overall efficiency**.

If you just want to get started, we recommend our [UI demo](https://demo.argilla.io/sign-in?auth=ZGVtbzoxMjM0NTY3OA%3D%3D) or our [free Hugging Face Spaces deployment integration](https://huggingface.co/new-space?template=argilla/argilla-template-space). Curious, and want to know more? Read our [documentation](https://argilla-io.github.io/argilla/latest/).

## Why use Argilla?

Whether you are working on monitoring and improving complex **generative tasks** involving LLM pipelines with RAG, or you are working on a **predictive task** for things like AB-testing of span- and text-classification models. Our versatile platform helps you ensure **your data work pays off**.

### Improve your AI output quality through data quality

Compute is expensive and output quality is important. We help you focus on data, which tackles the root cause of both of these problems at once. Argilla helps you to **achieve and keep high-quality standards** for your data. This means you can improve the quality of your AI output.

### Take control of your data and models

Most AI platforms are black boxes. Argilla is different. We believe that you should be the owner of both your data and your models. That's why we provide you with all the tools your team needs to **manage your data and models in a way that suits you best**.

### Improve efficiency by quickly iterating on the right data and models

Gathering data is a time-consuming process. Argilla helps by providing a platform that allows you to **interact with your data in a more engaging way**. This means you can quickly and easily label your data with filters, AI feedback suggestions and semantic search. So you can focus on training your models and monitoring their performance.

## 🏘️ Community

We are an open-source community-driven project and we love to hear from you. Here are some ways to get involved:

- [Community Meetup](https://lu.ma/embed-checkout/evt-IQtRiSuXZCIW6FB): listen in or present during one of our bi-weekly events.

- [Slack](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g): get direct support from the community.

- [Roadmap](https://github.com/orgs/argilla-io/projects/10/views/1): plans change but we love to discuss those with our community so feel encouraged to participate.

## What do people build with Argilla?

### Open-source datasets and models

Argilla is a tool that can be used to achieve and keep **high-quality data standards** with a **focus on NLP and LLMs**. Our community uses Argilla to create amazing open-source [datasets](https://huggingface.co/datasets?other=argilla) and [models](https://huggingface.co/models?other=distilabel), and **we love contributions to open-source** ourselves too.

- Our [cleaned UltraFeedback dataset](https://huggingface.co/datasets/argilla/ultrafeedback-binarized-preferences-cleaned) and the [Notus](https://huggingface.co/argilla/notus-7b-v1) and [Notux](https://huggingface.co/argilla/notux-8x7b-v1) models, where we improved benchmark and empirical human judgment for the Mistral and Mixtral models with cleaner data using **human feedback**.
- Our [distilabeled Intel Orca DPO dataset](https://huggingface.co/datasets/argilla/distilabel-intel-orca-dpo-pairs) and the [improved OpenHermes model](https://huggingface.co/argilla/distilabeled-OpenHermes-2.5-Mistral-7B), show how we improve model performance by filtering out 50% of the original dataset through **human and AI feedback**.

### Internal Use cases

AI teams from companies like [the Red Cross](https://510.global/), [Loris.ai](https://loris.ai/) and [Prolific](https://www.prolific.com/) use Argilla to **improve the quality and efficiency of AI** projects. They shared their experiences in our [AI community meetup](https://lu.ma/embed-checkout/evt-IQtRiSuXZCIW6FB).

- AI for good: [the Red Cross presentation](https://youtu.be/ZsCqrAhzkFU?feature=shared) showcases **how their experts and AI team collaborate** by classifying and redirecting requests from refugees of the Ukrainian crisis to streamline the support processes of the Red Cross.
- Customer support: during [the Loris meetup](https://youtu.be/jWrtgf2w4VU?feature=shared) they showed how their AI team uses unsupervised and few-shot contrastive learning to help them **quickly validate and gain labelled samples for a huge amount of multi-label classifiers**.
- Research studies: [the showcase from Prolific](https://youtu.be/ePDlhIxnuAs?feature=shared) announced their integration with our platform. They use it to actively **distribute data collection projects** among their annotating workforce. This allows them to quickly and **efficiently collect high-quality data** for their research studies.

## 🖥️ FRONTEND

<h3>💣 Install dependencies</h3>

```bash
npm i
```

<hr>

<h3>🚀 Run Locally</a></h3>

```bash
npm run dev
```

<hr>

<h3>🌏 Build Locally</a></h3>

```bash
npm run generate
```

## 📏 Principles

- **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.

- **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.

- **User and Developer Experience**: The key to sustainable NLP solutions are to make it easier for everyone to contribute to projects. _Domain experts_ should feel comfortable interpreting and annotating data. _Data scientists_ should feel free to experiment and iterate. _Engineers_ should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.

- **Beyond hand-labeling**: Classical hand-labeling workflows are costly and inefficient, but having humans in the loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak supervision in **novel** data annotation workflows\*\*.

## 🫱🏾‍🫲🏼 Contribute

To help our community with the creation of contributions, we have created our [community](https://argilla-io.github.io/argilla/latest/community/) docs. Additionally, you can always [schedule a meeting](https://calendly.com/david-berenstein-huggingface/30min) with our Developer Advocacy team so they can get you up to speed.

<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>

## 🗺️ Roadmap

We continuously work on updating [our plans and our roadmap](https://github.com/orgs/argilla-io/projects/10/views/1) and we love to discuss those with our community. Feel encouraged to participate.
