<p align="center">
    <img src="docs/images/rubrix_logo.svg" alt="drawing" width="225"/>
</p>

# Open-source tool for tracking and evolving data for AI

<p align="center">
    <a href="https://github.com/recognai/rubrix/actions">
        <img alt="CI" src="https://github.com/recognai/rubrix/workflows/CI/badge.svg?branch=master&event=push">
    </a>
    <!--a href="https://github.com/recognai/rubrix/blob/master/LICENSE">
        <img alt="GitHub" src="https://img.shields.io/github/license/recognai/rubrix.svg?color=blue">
    </a-->
</p>


Rubrix is a tool for tracking and iterating on data for artificial intelligence projects. Rubrix focuses on enabling novel, human in the loop workflows involving data scientists, subject matter experts and ML/data engineers. 

![](docs/images/rubrix_intro.svg)

With Rubrix, you can:

- **Monitor** the predictions of deployed models.
- **Collect** ground-truth data for starting up a project or evolving an existing one.
- **Iterate** on ****ground-truth data**** and predictions to debug, track and improve your models over time.
- **Build** custom ****applications and dashboards**** on top of your model predictions.

We've tried to make working with Rubrix easy and fun, while keeping it scalable and flexible. Rubrix is composed of:

- a **web application and a REST API**, which you can launch using Docker or build it yourself.
- a **Python library** to bridge data and models, which you can install via `pip`.

For further information, please visit [Rubrix documentation](https://docs.rubrix.ml/en/latest/)

# Get started

## 1. Launch your Rubrix app

### 1a. Using Docker and docker-compose

```bash
wget -O docker-compose.yml https://raw.githubusercontent.com/recognai/rubrix/master/docker-compose.yaml && docker-compose up
```
### 1b. With a local or remote Elasticsearch instance

1. ([https://www.elastic.co/guide/en/elasticsearch/reference/7.12/install-elasticsearch.html](Install) and) launch your Elasticsearch instance. 

2. Install the Rubrix Python library with server code `pip install rubrix[server]==0.1.0b2`.

3. Launch a local instance of Rubrix app: `python -m rubrix.server`. 

To see if everything went as expected go to [http://localhost:6900/](http://localhost:6900/).

You can also view the API docs at [http://localhost:6900/api/docs](http://localhost:6900/api/docs).
## 2. Install the Rubrix Python library:

If you are using a local installation (1b), you can skip this part.

```bash
pip install rubrix
```

## 3. Start logging data

The following code will log one record into the `example-dataset` dataset: 

```python
import rubrix as rb

rb.log(
    rb.TextClassificationRecord(inputs={"text": "my first rubrix example"}),
    name='example-dataset'
)

```

```bash
BulkResponse(dataset='example-dataset', processed=1, failed=0)
```

If you go to your Rubrix app at [http://localhost:6900/](http://localhost:6900/), you should see your first dataset.

Congratulations! You are ready to start working with Rubrix with your own data. To better understand what's possible take a look at our tutorials at: [https://github.com/recognai/rubrix/tree/master/docs/tutorials](https://github.com/recognai/rubrix/tree/master/docs/tutorials)

