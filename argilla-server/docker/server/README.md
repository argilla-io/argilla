<h1 align="center">
  <a href=""><img src="https://github.com/dvsrepo/imgs/raw/main/rg.svg" alt="Argilla" width="150"></a>
  <br>
  Argilla
  <br>
</h1>


Argilla is a **collaboration tool for AI engineers and domain experts** that require **high-quality outputs, data ownership, and overall efficiency**.

## Why use Argilla?

Whether you are working on monitoring and improving complex **generative tasks** involving LLM pipelines with RAG, or you are working on a **predictive task** for things like AB-testing of span- and text-classification models. Our versatile platform helps you ensure **your data work pays off**.


### Environment variables

Besides the common environment variables defined in docs, this Docker image provides a set of variables to simplify the server startup:
:

- `USERNAME`: If provided, the owner username. This can be combined with HF OAuth to define the argilla server owner (Default: `""`).

- `PASSWORD`: If provided, the owner password. If `USERNAME` and `PASSWORD` are provided, the owner user will be created with these credentials on the server startup (Default: `""`).

- `API_KEY`: If provided, the owner api key. When `USERNAME` and `PASSWORD` are provided and `API_KEY` is empty, a new random value will be generated (Default: `""`).

- `REINDEX_DATASET`: If `true` or `1`, the datasets will be reindexed in the search engine. This is needed when some search configuration changed or data must be refreshed (Default: `0`).
