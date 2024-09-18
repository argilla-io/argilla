We support different tasks within the Argilla eco-system focused on NLP: `Text Classification`, `Token Classification`, `Text2Text` and LLM-related `Feedback`. To know more about creation, take a look [here](/practical_guides/create_update_dataset/create_dataset.md).


::::{tab-set}

:::{tab-item} Feedback Task

```python
import argilla as rg

record = rg.FeedbackRecord(
    fields={
        "question": "Why can camels survive long without water?",
        "answer": "Camels use the fat in their humps to keep them filled with energy and hydration for long periods of time."
    },
    metadata={"source": "encyclopedia"},
    external_id='rec_1'
)
```

![text2text_record](/_static/images/llms/feedback-record.jpeg)
:::


:::{tab-item} Text Classification

```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text="beautiful accomodations stayed hotel santa... hotels higer ranked website.",
    prediction=[("price", 0.75), ("hygiene", 0.25)],
    annotation="price"
)
rg.log(records=rec, name="my_dataset")
```
![single_textclass_record](/_static/reference/webapp/features-single_textclass_record.png)
:::

:::{tab-item} Text Classification (multi-label)
```python
import argilla as rg

rec = rg.TextClassificationRecord(
    text="damn this kid and her fancy clothes makes me feel like a bad parent.",
    prediction=[("admiration", 0.75), ("annoyance", 0.25)],
    annotation=["price", "annoyance"],
    multi_label=True
)
rg.log(records=rec, name="my_dataset")
```
![multi_textclass_record](/_static/reference/webapp/features-multi_textclass_record.png)
:::


:::{tab-item} Token Classification
```python
import argilla as rg

record = rg.TokenClassificationRecord(
    text="Michael is a professor at Harvard",
    tokens=["Michael", "is", "a", "professor", "at", "Harvard"],
    prediction=[("NAME", 0, 7, 0.75), ("LOC", 26, 33, 0.8)],
    annotation=[("NAME", 0, 7), ("LOC", 26, 33)],
)
rg.log(records=rec, name="my_dataset")
```
![tokclass_record](/_static/reference/webapp/features-tokclass_record.png)
:::

:::{tab-item} Text2Text
```python
import argilla as rg

record = rg.Text2TextRecord(
    text="A giant giant spider is discovered... how much does he make in a year?",
    prediction=["He has 3*4 trees. So he has 12*5=60 apples."],
)
rg.log(records=rec, name="my_dataset")
```

![text2text_record](/_static/reference/webapp/features-text2text_record.png)
:::

::::