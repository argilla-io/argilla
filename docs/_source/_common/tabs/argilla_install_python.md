First things first! You can use a basic `pip install` to install for `pypi` but we also provide some custom extras and more developer-related installment options.

::::{tab-set}

:::{tab-item} Without extras
```bash
pip install argilla
```
:::

:::{tab-item} With extras
```
pip install argilla[listeners] # use argilla.listeners background processes
pip install argilla[server] # running FastAPI locally
pip install argilla[postgresql] # use PostgreSQL instead of SQLite as database
pip install argilla[integrations] # use integrations with other libraries/frameworks
pip install argilla[tests] # running tests locally
```
:::

:::{tab-item} From `develop`
```
pip install -U git+https://github.com/argilla-io/argilla.git
```
:::
::::