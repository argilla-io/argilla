
<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  ✨ Argilla ✨
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
<a  href="https://huggingface.co/new-space?template=argilla/argilla-template-space">
<img src="https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-sm.svg" />
</a>
</p>

<h2 align="center">Open-source data curation platform for LLMs</h2>
<h3 align="center">MLOps for NLP: from data labeling to model monitoring</h2>

<br>


https://github.com/argilla-io/argilla/assets/1107111/49e28d64-9799-4cac-be49-19dce0f6bd86

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
<a href="https://docs.argilla.io">📄 Documentation</a> | </span>
<a href="#-quickstart">🚀 Quickstart</a> <span> | </span>
<a href="#-cheatsheet">🎼 Cheatsheet</a> <span> | </span>
<a href="#-principles">📏 Principles</a> | </span>
<a href="#-contribute">🫱🏾‍🫲🏼 Contribute</a>
</p>
</h3>

## 🚀 Quickstart

Argilla is an open-source data curation platform for LLMs. Using Argilla, everyone can build robust language models through faster data curation using both human and machine feedback. We provide support for each step in the MLOps cycle, from data labeling to model monitoring.

There are different options to get started:

1. Take a look at our [quickstart page](https://docs.argilla.io/en/latest/getting_started/quickstart.html) 🚀

2. Start contributing by looking at our [contributor guidelines](#🫱🏾‍🫲🏼-contribute) 🫱🏾‍🫲🏼

3. Skip some steps with our [cheatsheet](#🎼-cheatsheet) 🎼

## 🎼 Cheatsheet


<h3><a href="https://docs.argilla.io/en/latest/getting_started/installation/deployments/docker-quickstart.html"> Deploy Locally</a></h3>


```bash
docker run -d --name argilla -p 6900:6900 argilla/argilla-quickstart:latest
```

<hr>
<h3><a href="https://argilla.io/blog/launching-argilla-huggingface-hub/">Deploy on Hugging Face Hub</a></h3>

<a href="https://argilla.io/blog/launching-argilla-huggingface-hub/"><img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/spaces-argilla-embed-space.png" width="100%"></a>

<hr>
<h3><a href="https://docs.argilla.io/en/latest/guides/guides/llms/conceptual_guides/conceptual_guides.html">LLM support</a></h3>

```python
import argilla as rg

dataset = rg.FeedbackDataset(
    guidelines="Please, read the question carefully and try to answer it as accurately as possible.",
    fields=[
        rg.TextField(name="question"),
        rg.TextField(name="answer"),
    ],
    questions=[
        rg.RatingQuestion(
            name="answer_quality",
            description="How would you rate the quality of the answer?",
            values=[1, 2, 3, 4, 5],
        ),
        rg.TextQuestion(
            name="answer_correction",
            description="If you think the answer is not accurate, please, correct it.",
            required=False,
        ),
    ]
)
```

<a href="https://docs.argilla.io/en/latest/guides/guides/llms/conceptual_guides/conceptual_guides.html"><img src="https://docs.argilla.io/en/latest/_images/snapshot-feedback-demo.png" width="100%"></a>

<hr>
<h3><a href="https://docs.argilla.io/en/latest/guides/log_load_and_prepare_data.html#Argilla-Records">Create Records</a></h3>


```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text="Sun Is Closer... a parachute.",
    prediction=[("Sci/Tech", 0.75), ("World", 0.25)],
    annotation="Sci/Tech"
)
rg.log(records=record, name="news")
```

<a href="https://docs.argilla.io/en/latest/guides/log_load_and_prepare_data.html#Argilla-Records"><img src="https://docs.argilla.io/en/latest/_images/features-annotate.png" width="100%"></a>

<hr>
<h3><a href="https://docs.argilla.io/en/latest/guides/query_datasets.html">Query datasets</a></h3>


```python
import argilla as rg

rg.load(name="news", query="text:spor*")
```

<a href="https://docs.argilla.io/en/latest/guides/query_datasets.html"><img src="https://docs.argilla.io/en/latest/_images/features-search.png" width="100%">

<hr>
<h3><a href="https://docs.argilla.io/en/latest/guides/label_records_with_semanticsearch.html">Semantic search</a></h3>

```python
import argilla as rg

record = rg.TextClassificationRecord(
    text="Hello world, I am a vector record!",
    vectors= {"my_vector_name": [0, 42, 1984]}
)
rg.log(name="dataset", records=record)
rg.load(name="dataset", vector=("my_vector_name", [0, 43, 1985]))
```

<a href="https://docs.argilla.io/en/latest/guides/label_records_with_semanticsearch.html"><img src="https://docs.argilla.io/en/latest/_images/features-similaritysearch.png" width="100%"></a>

<hr>
<h3><a href="https://docs.argilla.io/en/latest/guides/programmatic_labeling_with_rules.html">Weak supervision</a></h3>


```python
from argilla.labeling.text_classification import add_rules, Rule

rule = Rule(query="positive impact", label="optimism")
add_rules(dataset="go_emotion", rules=[rule])
```

<a href="https://docs.argilla.io/en/latest/guides/programmatic_labeling_with_rules.html"><img src="https://docs.argilla.io/en/latest/_images/features-weak-labelling.png" width="100%"></a>

<!-- <tr>
<td>
<a href="https://argilla.io/blog/introducing-argilla-trainer">Active Learning</a>
</td>
<td>

```python
from argilla_plugins import classy_learner

plugin = classy_learner(name="plugin-test")
plugin.start()
```

<video src="https://share.descript.com/view/nvlUjF8tNcZ"/>
</td>
</tr> -->

<hr>
<h3><a href="https://argilla.io/blog/introducing-argilla-trainer">Train models</a></h3>

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(name="news", workspace="recognai", framework="setfit")
trainer.train()
```

<a href="https://argilla.io/blog/introducing-argilla-trainer"><img src="https://argilla.io/blog/introducing-argilla-trainer/train.png" width="100%"></a>



## 📏 Principles
-  **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.



-  **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.



-  **User and Developer Experience**: The key to sustainable NLP solutions are to make it easier for everyone to contribute to projects. _Domain experts_ should feel comfortable interpreting and annotating data. _Data scientists_ should feel free to experiment and iterate. _Engineers_ should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.



-  **Beyond hand-labeling**: Classical hand-labeling workflows are costly and inefficient, but having humans in the loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak supervision in **novel** data annotation workflows**.

## 🫱🏾‍🫲🏼 Contribute

We love contributors and have launched a [collaboration with JustDiggit](https://argilla.io/blog/introducing-argilla-community-growers) to hand out our very own bunds and help the re-greening of sub-Saharan Africa. To help our community with the creation of contributions, we have created our [developer](https://docs.argilla.io/en/latest/community/developer_docs.html) and [contributor](https://docs.argilla.io/en/latest/community/contributing.html) docs. Additionally, you can always [schedule a meeting](https://calendly.com/argilla-office-hours/meeting-with-david-from-argilla-30m) with our Developer Advocacy team so they can get you up to speed.

## 🥇 Contributors
<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>
