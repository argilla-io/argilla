The data required for these steps need to be used as comparison data to showcase the preference for the generated prompts. A good example is our [curated Dolly dataset](https://huggingface.co/datasets/argilla/databricks-dolly-15k-curated-en), where we assumed that updated responses get preference over the older ones. Another good example is the [Anthropic RLHF dataset](https://huggingface.co/datasets/Anthropic/hh-rlhf).

```{note}
The Dolly original dataset contained a lot of reference indicators such as "[1]", which causes the model to hallucinate and incorrectly create references.
```

::::{tab-set}

:::{tab-item} Original

```
### Instruction
When did Virgin Australia start operating?

### Context
Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline.
It is the largest airline by fleet size to use the Virgin brand. [2]
It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.[3]
It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001.
The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.[4]

### Response:
Virgin Australia commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
```

:::

:::{tab-item} Corrected

```
### Instruction
When did Virgin Australia start operating?

### Context
Virgin Australia, the trading name of Virgin Australia Airlines Pty Ltd, is an Australian-based airline.
It is the largest airline by fleet size to use the Virgin brand.
It commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
It suddenly found itself as a major airline in Australia's domestic market after the collapse of Ansett Australia in September 2001.
The airline has since grown to directly serve 32 cities in Australia, from hubs in Brisbane, Melbourne and Sydney.

### Response:
Virgin Australia commenced services on 31 August 2000 as Virgin Blue, with two aircraft on a single route.
```

:::

::::
