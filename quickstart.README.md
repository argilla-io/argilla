<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  Argilla
  <br>
</h1>
<p align="center">
<a  href="https://pypi.org/project/argilla/">
<img  alt="CI"  src="https://img.shields.io/pypi/v/argilla.svg?style=flat-square&logo=pypi&logoColor=white">
</a>
<!--a  href="https://anaconda.org/conda-forge/rubrix">
<img  alt="CI"  src="https://img.shields.io/conda/vn/conda-forge/rubrix?logo=anaconda&style=flat&color=orange">
</!a-->
<img alt="Codecov" src="https://codecov.io/gh/argilla-io/argilla/branch/main/graph/badge.svg?token=VDVR29VOMG"/>
<a href="https://pepy.tech/project/argilla">
<img  alt="CI"  src="https://static.pepy.tech/personalized-badge/argilla?period=month&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads/month">
</a>
</p>

<h2 align="center">Open-source framework for data-centric NLP</h2>
<p align="center">Data Labeling, curation, and Inference Store</p>
<p align="center">Designed for MLOps & Feedback Loops</p>


> 🆕 🔥 Play with Argilla UI with this [live-demo](https://argilla-live-demo.hf.space) powered by Hugging Face Spaces (
> login:`argilla`, password:`1234`)

> 🆕 🔥 Since `1.2.0` Argilla supports vector search for finding the most similar records to a given one. This feature
> uses vector or semantic search combined with more traditional search (keyword and filter based). Learn more on
> this [deep-dive guide](https://docs.argilla.io/en/latest/guides/features/semantic-search.html)


![imagen](https://user-images.githubusercontent.com/1107111/204772677-facee627-9b3b-43ca-8533-bbc9b4e2d0aa.png)

<!-- https://user-images.githubusercontent.com/25269220/200496945-7efb11b8-19f3-4793-bb1d-d42132009cbb.mp4 -->


<p align="center">
<a  href="https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g">
<img src="https://img.shields.io/badge/JOIN US ON SLACK-4A154B?style=for-the-badge&logo=slack&logoColor=white" />
</a>
<a href="https://linkedin.com/company/argilla-io">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />
</a>
<a  href="https://twitter.com/argilla_io">
<img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" />
</a>
</p>

<br>

<h3>
<p align="center">
<a href="https://docs.argilla.io">Documentation</a> | </span>
<a href="#key-features">Key Features</a> <span> | </span>
<a href="#quickstart">Quickstart</a> <span> | </span>
<a href="#principles">Principles</a> | </span>
<a href="docs/_source/community/migration-rubrix.md">Migration from Rubrix</a> | </span>
<a href="#faq">FAQ</a>
</p>
</h3>

## Key Features

### Advanced NLP labeling

- Programmatic labeling
  using [weak supervision](https://docs.argilla.io/en/latest/guides/techniques/weak_supervision.html). Built-in label
  models (Snorkel, Flyingsquid)
- [Bulk-labeling](https://docs.argilla.io/en/latest/reference/webapp/features.html#bulk-annotate)
  and [search-driven annotation](https://docs.argilla.io/en/latest/guides/features/queries.html)
- Iterate on training data with
  any [pre-trained model](https://docs.argilla.io/en/latest/tutorials/libraries/huggingface.html)
  or [library](https://docs.argilla.io/en/latest/tutorials/libraries/libraries.html)
- Efficiently review and refine annotations in the UI and with Python
- Use Argilla built-in metrics and methods
  for [finding label and data errors (e.g., cleanlab)](https://docs.argilla.io/en/latest/tutorials/notebooks/monitoring-textclassification-cleanlab-explainability.html)
- Simple integration
  with [active learning workflows](https://docs.argilla.io/en/latest/tutorials/techniques/active_learning.html)

### Monitoring

- Close the gap between production data and data collection activities
- [Auto-monitoring](https://docs.argilla.io/en/latest/guides/steps/3_deploying.html)
  for [major NLP libraries and pipelines](https://docs.argilla.io/en/latest/tutorials/libraries/libraries.html) (spaCy,
  Hugging Face, FlairNLP)
- [ASGI middleware](https://docs.argilla.io/en/latest/tutorials/notebooks/deploying-texttokenclassification-fastapi.html)
  for HTTP endpoints
- Argilla Metrics to understand data and model
  issues, [like entity consistency for NER models](https://docs.argilla.io/en/latest/guides/steps/4_monitoring.html)
- Integrated with Kibana for custom dashboards

### Team workspaces

- Bring different users and roles into the NLP data and model lifecycles
- Organize data collection, review and monitoring into
  different [workspaces](https://docs.argilla.io/en/latest/getting_started/installation/user_management.html#workspace)
- Manage workspace access for different users

## Quickstart

Argilla is composed of a Python Server with Elasticsearch as the database layer, and a Python Client to create and
manage datasets.

To get started you just need to run the docker image with following command:

``` bash
  docker run -d --name quickstart -p 6900:6900 argilla/argilla-quickstart:latest
```

This will run the latest quickstart docker image with 2 users `argilla` and `team`. The password for these users is
`1234` . You can also configure these [environment variables](#environment-variables) as per you needs.

### Environment Variables

- `ARGILLA_API_KEY`: Argilla provides a Python library to interact with the app (read, write, and update data, log model
  predictions, etc.). If you don't set this variable, the library and your app will use the default API key. If you want
  to secure your app for reading and writing data, we recommend you to set up this variable. The API key you choose
  can be any string of your choice and you can check an online generator if you like.
- `ARGILLA_PASSWORD`: This sets a custom password for login into the app with the `argilla` username. The default
  password is `1234`. By setting up a custom password you can use your own password to login into the app.
- `TEAM_API_KEY`: This sets the root user's API key. The API key you choose can be any string of your choice and you can
  check an online generator if you like.
- `TEAM_PASSWORD`: This sets a custom password for login into the app with the `argilla` username. The default password
  is `1234`. By setting up a custom password you can use your own password to login into the app.
