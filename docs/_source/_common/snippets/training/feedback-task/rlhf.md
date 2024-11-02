---
title: RLHF
description: Reinforcement Learning with Human Feedback (RLHF) proved to be the driving force behind the power of ChatGPT and other LLMs. Argilla does provides an integration for Reinforcement Learning with Human Feedback (RLHF) with the ArgillaTrainer class. Generally, this is done in three steps (1) SFT, (2) Reward Modeling and (3) PPO.
links:
  - linkText: Practical guide to SFT
    linkLink: https://docs.v1.argilla.io/en/latest/guides/llms/practical_guides/fine_tune.html#supervised-finetuning
  - linkText: Practical Guide to Reward Modeling
    linkLink: https://docs.v1.argilla.io/en/latest/guides/llms/practical_guides/fine_tune.html#reward-modeling
  - linkText: Practical Guide to PPO
    linkLink: https://docs.v1.argilla.io/en/latest/guides/llms/practical_guides/fine_tune.html#proximal-policy-optimization
---

```python
from argilla.feedback import ArgillaTrainer, FeedbackDataset, TrainingTask

dataset = FeedbackDataset.from_argilla(
    name="<my_dataset_name>",
    workspace="<my_workspace_name>"
)
template = """\
### Instruction: {instruction}\n
### Context: {context}\n
### Response: {response}"""

def formatting_func_sft(sample: Dict[str, Any]) -> str:
    # What `sample` looks like depends a lot on your FeedbackDataset fields and questions
    return template.format(
        instruction=sample["new-instruction"][0]["value"],
        context=sample["new-context"][0]["value"],
        response=sample["new-response"][0]["value"],
    )
task = TrainingTask.for_supervised_fine_tuning(formatting_func=formatting_func)

def formatting_func_rm(sample: Dict[str, Any]) -> Iterator[Tuple[str, str]]:
    # Our annotators were asked to provide new responses, which we assume are better than the originals
    og_instruction = sample["original-instruction"]
    og_context = sample["original-context"]
    og_response = sample["original-response"]
    rejected = template.format(instruction=og_instruction, context=og_context, response=og_response)

    for instruction, context, response in zip(sample["new-instruction"], sample["new-context"], sample["new-response"]):
        if response["status"] == "submitted":
            chosen = template.format(
                instruction=instruction["value"],
                context=context["value"],
                response=response["value"],
            )
            if chosen != rejected:
                yield chosen, rejected
task = TrainingTask.for_reward_modeling(formatting_func=formatting_func)

def formatting_func(sample: Dict[str, Any]) -> Iterator[str]:
    for instruction, context in zip(sample["new-instruction"], sample["new-context"]):
        if instruction["status"] == "submitted":
            yield template.format(
                instruction=instruction["value"],
                context=context["value"][:500],
                response=""
            ).strip()
task = TrainingTask.for_proximal_policy_optimization(formatting_func=formatting_func)

trainer = ArgillaTrainer(
    dataset=dataset,
    task=task,
    framework="trl",
)
trainer.update_config()
trainer.train()
```