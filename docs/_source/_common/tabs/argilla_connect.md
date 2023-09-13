::::{tab-set}

:::{tab-item} Default
By default Argilla connects to `localhost:6900` using the `argilla.apikey` in the background.
:::

:::{tab-item} Environment Variables

```bash
# MacOS
export ARGILLA_API_URL="argilla-api-url"
export ARGILLA_API_KEY="argilla-api-key"

# Windows
setx ARGILLA_API_URL="argilla-api-url"
setx ARGILLA_API_URL="argilla-api-key"
```

:::

:::{tab-item} rg.init()
```python
import argilla as rg

rg.init(
    api_url="argilla-api-url",
    api_key="argilla-api-key"
)
```
:::

:::{tab-item} local client
```python
from argilla.client.client import Argilla

client = Argilla(
    api_url="argilla-api-url",
    api_key="argilla-api-key"
)
```
:::

:::{tab-item} CLI

From `1.16.0` version you can use the CLI to connect to an Argilla server.

First login to the Argilla server using the CLI

```sh
argilla login --api-url http://localhost:6900 --api-key argilla.apikey
```

Then call `init` function without arguments to use the stored credentials created by the `login` command

```python
import argilla as rg

rg.init()
```
:::

::::
