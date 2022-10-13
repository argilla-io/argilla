# Quickstart

Getting started with Argilla is easy, let's see a quick example using the 🤗 `transformers` and `datasets` Libraries

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

:::{note}
The most common error message after this step is related to the Elasticsearch instance not running. Make sure your Elasticsearch instance is running on http://localhost:9200/. If you already have an Elasticsearch instance or cluster, you point the server to its URL by using ENV variables.
:::


🎉 You can now access Argilla UI pointing your browser at [http://localhost:6900/](http://localhost:6900/). **The default username and password are** `argilla` **and** `1234`.

> 🚒 **If you find issues, get direct support from the team and other community members on the [Slack Community](https://join.slack.com/t/rubrixworkspace/shared_invite/zt-whigkyjn-a3IUJLD7gDbTZ0rKlvcJ5g)**


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

Let's filter the records predicted as `Sports` with high probability and use the bulk-labeling feature for labeling 5 records as `Sports`.

After a few iterations of data annotation, we can load the Argilla dataset and create a training set to train or fine-tune a supervised model. You can do this using `rg.load` method and the different serialization methods (`prepare_for_training` for transformers and spaCy, `to_pandas` for other packages such as sklearn).