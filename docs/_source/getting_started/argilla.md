# What is Argilla?

[Argilla](https://argilla.io) is a **production-ready framework for building and improving datasets** for NLP projects.


<video width="100%" controls><source src="/_static/tutorials/labelling-textclassification-snorkel-weaksupervision/ws_news.mp4" type="video/mp4"></video>


## Features

- **Open**: Argilla is free, open-source, and 100% compatible with major NLP libraries (Hugging Face transformers, spaCy, Stanford Stanza, Flair, etc.). In fact, you can **use and combine your preferred libraries** without implementing any specific interface.

- **End-to-end**: Most annotation tools treat data collection as a one-off activity at the beginning of each project. In real-world projects, data collection is a key activity of the iterative process of ML model development. Once a model goes into production, you want to monitor and analyze its predictions, and collect more data to improve your model over time. Argilla is designed to close this gap, enabling you to **iterate as much as you need**.

- **User and Developer Experience**: The key to sustainable NLP solutions is to make it easier for everyone to contribute to projects. *Domain experts* should feel comfortable interpreting and annotating data. *Data scientists* should feel free to experiment and iterate. *Engineers* should feel in control of data pipelines. Argilla optimizes the experience for these core users to **make your teams more productive**.

- **Beyond hand-labeling**: Classical hand labeling workflows are costly and inefficient, but having humans-in-the-loop is essential. Easily combine hand-labeling with active learning, bulk-labeling, zero-shot models, and weak-supervision in **novel data annotation workflows**.


## Quickstart

Getting started with Argilla is easy, let's see a quick example using the 🤗 `transformers` and `datasets` libraries:

{{ '```bash\npip install "argilla[server]{}" "transformers[torch]" datasets\n```'.format(pipversion) }}

If you don't have [Elasticsearch (ES)](https://www.elastic.co/elasticsearch) running, make sure you have `docker` installed and run:

:::{note}
Check the [setup and installation section](setup-and-installation) for further options and configurations regarding Elasticsearch.
:::

```bash
docker run -d --name elasticsearch-for-argilla -p 9200:9200 -p 9300:9300 -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
```

Then simply run:

```bash
python -m argilla
```

Afterward, you should be able to access the web app at <http://localhost:6900/>.
**The default username and password are** `argilla` **and** `1234`.

> 🚒  **If you have problems launching Argilla, you can get direct support from the maintainers and other community member by joining [Argilla's Slack Community](https://join.slack.com/t/argillaworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**

Now, let's see an example: **Bootstraping data annotation with a zero-shot classifier**

**Why**:

- The availability of pre-trained language models with zero-shot capabilities means you can, sometimes, accelerate your data annotation tasks by pre-annotating your corpus with a pre-trained zero-shot model.
- The same workflow can be applied if there is a pre-trained "supervised" model that fits your categories but needs fine-tuning for your own use case. For example, fine-tuning a sentiment classifier for a very specific type of message.

**Ingredients**:

- A zero-shot classifier from the 🤗 Hub: `typeform/distilbert-base-uncased-mnli`
- A dataset containing news
- A set of target categories: `Business`, `Sports`, etc.

**What are we going to do**:

1. Make predictions and log them into a Argilla dataset.
2. Use the Argilla web app to explore, filter, and annotate some examples.
3. Load the annotated examples and create a training set, which you can then use to train a supervised classifier.


Use your favourite editor or a Jupyter notebook to run the following:

```python
 from transformers import pipeline
 from datasets import load_dataset
 import argilla as rg

 model = pipeline('zero-shot-classification', model="typeform/squeezebert-mnli")

 dataset = load_dataset("ag_news", split='test[0:100]')

 labels = ['World', 'Sports', 'Business', 'Sci/Tech']

 records = []
 for record in dataset:
     prediction = model(record['text'], labels)

     records.append(
         rg.TextClassificationRecord(
             text=record["text"],
             prediction=list(zip(prediction['labels'], prediction['scores'])),
         )
     )

 rg.log(records, name="news_zeroshot")
```


Now you can explore the records in the Argilla UI at <http://localhost:6900/>.
**The default username and password are** `argilla` **and** `1234`.

Let's filter the records predicted as `Sports` with high probability and use the bulk-labeling feature for labeling 5 records as `Sports`:

![zero-shot example](/_static/images/main/zero_shot_example.png)

After a few iterations of data annotation, we can load the Argilla dataset and create a training set to train or fine-tune a supervised model.

```python
# load the Argilla dataset and put it into a pandas DataFrame
rg_df = rg.load(name='news_zeroshot').to_pandas()

# filter annotated records
rg_df = rg_df[rg_df.status == "Validated"]

# select text input and the annotated label
train_df = pd.DataFrame({
   "text": rg_df.text,
   "label": rg_df.annotation,
})
```

## Use cases

* **Data labelling and review**: collect labels to start a project from scratch or from existing live models.
* **Model monitoring and observability:** log and observe predictions of live models.
* **Evaluation**: easily compute "live" metrics from models in production, and slice evaluation datasets to test your system under specific conditions.
* **Model debugging**: log predictions during the development process to visually spot issues.
* **Explainability:** log token attributions to help you interpret model predictions.

## Community

You can join the conversation on Slack! We are a very friendly and inclusive community:

* [Slack community](https://join.slack.com/t/argillaworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)