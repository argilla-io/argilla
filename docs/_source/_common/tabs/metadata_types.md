::::{tab-set}

:::{tab-item} Terms

```python
rg.TermsMetadataProperty(
    name="groups",
    title="Annotation groups",
    values=["group-a", "group-b", "group-c"] #optional
)
```
:::
:::{tab-item} Integer

```python
rg.IntegerMetadataProperty(
    name="integer-metadata",
    title="Integers",
    min=0, #optional
    max=100, #optional
    visible_for_annotators=False
)
```
:::
:::{tab-item} Float

```python
rg.FloatMetadataProperty(
    name="float-metadata",
    title="Floats",
    min=-0.45, #optional
    max=1000.34, #optional
    visible_for_annotators=False
)
```
:::
::::