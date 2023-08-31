First things first! You can use a basic `pip install` to install for `pypi`, but we also provide some custom extras and more developer-related installment options.

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

:::{note}
Make sure you have the latest version of Argilla (and other packages) installed, so you can use all of the features!
To check which version you have, use `pip show argilla`. You can also install a specific version of the package
(by running `pip install argilla==1.11.0`, for example) or simply update to the latest version with `pip install argilla --upgrade`.
:::