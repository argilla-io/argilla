# Rubrix Streamlit demo app

**Rubrix** is an application and Python library for logging and exploring NLP experiment results. With it, you can:

- **Store**: efficiently store predictions, explanations and ground truth data.
- **Explore**: explore and analyze model predictions and errors.
- **Label**: collect labels from the UI or external apps.
- **Evaluate**: use collected labels to evaluate models.
- **Build**: use collected predictions to build external applications through a unified data model and REST API.

In this demo, we will show you how to initialize a Rubrix local environment and log your predictions on a zero-shot classifier about text categories, so you can start using Rubrix on your own experiments. By logging predictions into Rubrix, you can monitor your models, evaluate them, collect training data over time, and much more.

# Installing Rubrix

For the Python library, use the package manager [pip](https://pip.pypa.io/en/stable/) to install **Rubrix**

```bash
pip install rubrix
```

For more information about different types of installation, visit our Github Page [#TODO].

For the application setup, you will need to have [Docker](https://www.docker.com) and [docker compose](https://docs.docker.com/compose/)  installed in your system. We will use an already configured docker-compose file to start the local **Rubrix** stack. 

# Web App Dependencies

This demo web app uses a few other Python libraries. You can install all dependencies by running:

```bash
pip install -r requirements.txt
```

# Starting Rubrix locally

To start **Rubrix** stack locally:

1. Install rubrix or clone the git repository
```bash
git clone recognai/rubrix [TODO]
```

2. Launch Docker container from **Rubrix** root directory
```bash
docker-compose up 
```

3. Check the localhost is running at [http://localhost:6900/](http://localhost:6900/)


# Running the app
After starting **Rubrix** stack, you can run this Streamlit app from the root directory with

```bash
streamlit run docs/examples/streamlit-live/app.py
```

