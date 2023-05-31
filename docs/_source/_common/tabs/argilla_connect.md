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

::::