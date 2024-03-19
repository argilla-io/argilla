
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

If you just want to get started, we recommend our [UI demo](https://demo.argilla.io/sign-in?auth=ZGVtbzoxMjM0NTY3OA%3D%3D) or our [2-click deployment quick start](https://docs.argilla.io/en/latest/getting_started/cheatsheet.html). Curious, and want to know more? Read our [documentation](https://docs.argilla.io/).

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

## 👨‍💻 Getting started

<details>
<summary><a href="https://docs.argilla.io/en/latest/getting_started/installation/deployments/docker.html">pip install argilla</a></summary>
<p>

First things first! You can <a href="https://docs.argilla.io/en/develop/getting_started/installation/deployments/python.html">install Argilla</a> from pypi.

```bash
pip install argilla
```

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/getting_started/installation/deployments/docker.html">Deploy Locally</a></summary>
<p>

```bash
docker run -d --name argilla -p 6900:6900 argilla/argilla-quickstart:latest
```

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/develop/getting_started/installation/deployments/huggingface-spaces.html">Deploy on Hugging Face Hub</a></summary>
<p>

HuggingFace Spaces now have persistent storage and this is supported from Argilla 1.11.0 onwards, but you will need to manually activate it via the HuggingFace Spaces settings. Otherwise, unless you're on a paid space upgrade, after 48 hours of inactivity the space will be shut off and you will lose all the data. To avoid losing data, we highly recommend using the persistent storage layer offered by HuggingFace.

After this, we can connect to our server.

<a href="https://docs.argilla.io/en/develop/getting_started/installation/deployments/huggingface-spaces.html"><img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/spaces-argilla-embed-space.png" width="100%"></a>

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/getting_started/cheatsheet.html#connect-to-argilla">Connect to the Server</a></summary>
<p>
Once you have deployed Argilla, we will connect to the server.

```python
import argilla as rg

rg.init(
    api_url="argilla-api-url", # e.g. http://localhost:6900 or https://[your-owner-name]-[your_space_name].hf.space
    api_key="argilla-api-key" # e.g. "owner.apikey"
    workspace="argilla-workspace" # e.g. "admin"
)
```

After this, you can start using Argilla, so you can create a dataset and add records to it. We use the FeedbackDataset as an example, but you can use any of the other datasets available in Argilla. You can find more information about the different datasets <a href="https://docs.argilla.io/en/latest/practical_guides/choose_dataset.html">here</a>.

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/getting_started/installation/configurations/workspace_management.html#create-a-new-workspace">Create workspace</a></summary>
<p>
Once you have connected to the server, we will create a workspace for datasets.

```python
workspace = rg.Workspace.create("new-workspace")
```

After this, you can assign users to the workspace, this will allow the datasets to appear in the UI for that user.

```python
users = [u for u in rg.User.list() if u.role == "annotator"]
for user in users:
    workspace.add_user(user)
```

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/create_update_dataset/create_dataset.html">Configure datasets</a></summary>
<p>

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
remote_dataset = dataset.push_to_argilla(name="my-dataset", workspace="my-workspace")
```

<a href="https://docs.argilla.io/en/latest/practical_guides/create_dataset.html"><img src="https://docs.argilla.io/en/latest/_images/snapshot-feedback-demo.png" width="100%"></a>

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/records.html">Add records</a></summary>
<p>

```python
import argilla as rg

record = rg.FeedbackRecord(
    fields={
        "question": "Why can camels survive long without water?",
        "answer": "Camels use the fat in their humps to keep them filled with energy and hydration for long periods of time."
    },
    metadata={"source": "encyclopedia"},
    external_id='rec_1'
)
remote_dataset.add_records(record)
```

And that's it, you now have your first dataset ready. You can begin annotating it or embark on other related tasks.

<a href="https://docs.argilla.io/en/latest/practical_guides/records.html"><img src="https://docs.argilla.io/en/latest/_images/features-annotate.png" width="100%"></a>

</p>
</details>


<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html">Query datasets</a></summary>
<p>

```python
import argilla as rg

filtered_dataset = dataset.filter_by(response_status="submitted")
```

<a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html"><img src="https://docs.argilla.io/en/latest/_images/features-search.png" width="100%">

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html">Semantic search</a></summary>
<p>

```python
import argilla as rg

# using text embeddings
similar_records =  ds.find_similar_records(
    vector_name="my_vector",
    value=embedder_model.embeddings("My text is here")
    # value=embedder_model.embeddings("My text is here").tolist() # for numpy arrays
)

# using another record
similar_records =  ds.find_similar_records(
    vector_name="my_vector",
    record=ds.records[0],
    max_results=5
)
```

<a href="https://docs.argilla.io/en/latest/practical_guides/filter_dataset.html"><img src="https://docs.argilla.io/en/latest/_images/features-similaritysearch.png" width="100%"></a>

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/tutorials/techniques/weak_supervision.html">Weak supervision</a></summary>
<p>

```python
from argilla.labeling.text_classification import add_rules, Rule

rule = Rule(query="positive impact", label="optimism")
add_rules(dataset="go_emotion", rules=[rule])
```

<a href="https://docs.argilla.io/en/latest/tutorials/techniques/weak_supervision.html"><img src="https://docs.argilla.io/en/latest/_images/features-weak-labelling.png" width="100%"></a>

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

</p>
</details>

<details>
<summary><a href="https://docs.argilla.io/en/latest/practical_guides/fine_tune.html">Train models</a></summary>
<p>

```python
from argilla.training import ArgillaTrainer

trainer = ArgillaTrainer(
    name="my_dataset",
    workspace="my_workspace",
    framework="my_framework",
    model="my_framework_model",
    train_size=0.8,
    seed=42,
    limit=10,
    query="my-query"
)
trainer.update_config() # see usage below
trainer.train()
records = trainer.predict(["my-text"], as_argilla_records=True)
```

<a href="https://docs.argilla.io/en/latest/practical_guides/fine_tune.html"><img src="https://argilla.io/blog/introducing-argilla-trainer/train.png" width="100%"></a>

</p>
</details>

## 🥇 Contributors

We love contributors and have launched a [collaboration with JustDiggit](https://argilla.io/blog/introducing-argilla-community-growers) to hand out our very own bunds and help the re-greening of sub-Saharan Africa. To help our community with the creation of contributions, we have created our [developer](https://docs.argilla.io/en/latest/community/developer_docs.html) and [contributor](https://docs.argilla.io/en/latest/community/contributing.html) docs. Additionally, you can always [schedule a meeting](https://calendly.com/argilla-office-hours/30min) with our Developer Advocacy team so they can get you up to speed.

<a  href="https://github.com/argilla-io/argilla/graphs/contributors">

<img  src="https://contrib.rocks/image?repo=argilla-io/argilla" />

</a>

