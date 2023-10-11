#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import warnings
from typing import Any, Dict, List, Optional, Union

import torch
import torch.nn.functional as F
from packaging.version import parse
from transformers import TrainerCallback, TrainerControl, TrainerState
from transformers.training_args import TrainingArguments

import argilla as rg
from argilla.feedback import FeedbackDataset


class ArgillaTRLCallback(TrainerCallback):
    """Callback Handler that logs into Argilla.

    Args:
        dataset_name: name of the `FeedbackDataset` in Argilla. Note that it must
            exist in advance. If you need help on how to create a `FeedbackDataset` in
            Argilla, please visit
            https://docs.argilla.io/en/latest/guides/llms/practical_guides/use_argilla_callback_in_langchain.html.
        workspace_name: name of the workspace in Argilla where the specified
            `FeedbackDataset` lives in. Defaults to `None`, which means that the
            default workspace will be used.
        api_url: URL of the Argilla Server that we want to use, and where the
            `FeedbackDataset` lives in. Defaults to `None`, which means that either
            `ARGILLA_API_URL` environment variable or the default http://localhost:6900
            will be used.
        api_key: API Key to connect to the Argilla Server. Defaults to `None`, which
            means that either `ARGILLA_API_KEY` environment variable or the default
            `argilla.apikey` will be used.

    Raises:
        ImportError: if the `argilla` package is not installed.
        ConnectionError: if the connection to Argilla fails.
        FileNotFoundError: if the `FeedbackDataset` retrieval from Argilla fails.

    Examples:
        >>>
    """

    REPO_URL = "https://github.com/argilla-io/argilla"
    ISSUES_URL = f"{REPO_URL}/issues"

    DEFAULT_API_URL = "http://localhost:6900"
    DEFAULT_API_KEY = "argilla.apikey"

    def __init__(
        self,
        dataset_name: str,
        feedback_dataset: Optional[FeedbackDataset] = None,
        workspace_name: Optional[str] = None,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        generation_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        f"""Initializes the `ArgillaCallbackHandler`.

        Args:
            dataset_name: name of the `FeedbackDataset` in Argilla.
            feedback_dataset: The `FeedbackDataset` that will be used, must TODO.
                If not defined, a default `FeedbackDataset` will be created.
            workspace_name: name of the workspace in Argilla where the specified
                `FeedbackDataset` lives in. Defaults to `None`, which means that the
                default workspace will be used.
            api_url: URL of the Argilla Server that we want to use, and where the
                `FeedbackDataset` lives in. Defaults to `None`, which means that either
                `ARGILLA_API_URL` environment variable or `{self.DEFAULT_API_URL}` will
                be used.
            api_key: API Key to connect to the Argilla Server. Defaults to `None`, which
                means that either `ARGILLA_API_KEY` environment variable or the default
                `{self.DEFAULT_API_KEY}` will be used.

        Raises:
            ImportError: if the `argilla` package is not installed.
            ConnectionError: if the connection to Argilla fails.
            FileNotFoundError: if the `FeedbackDataset` retrieval from Argilla fails.
        """

        super().__init__()

        # Import Argilla (not via `import_argilla` to keep hints in IDEs)
        try:
            import argilla as rg  # noqa: F401

            self.ARGILLA_VERSION = rg.__version__
        except ImportError:
            raise ImportError(
                "To use the Argilla callback manager you need to have the `argilla` "
                "Python package installed. Please install it with `pip install argilla`"
            )

        # Check whether the Argilla version is compatible
        if parse(self.ARGILLA_VERSION) < parse("1.8.0"):
            raise ImportError(
                f"The installed `argilla` version is {self.ARGILLA_VERSION} but "
                "`ArgillaTRLCallback` requires at least version 1.8.0. Please "
                "upgrade `argilla` with `pip install --upgrade argilla`."
            )

        # Show a warning message if Argilla will assume the default values will be used
        if api_url is None and os.getenv("ARGILLA_API_URL") is None:
            warnings.warn(
                (
                    "Since `api_url` is None, and the env var `ARGILLA_API_URL` is not"
                    f" set, it will default to `{self.DEFAULT_API_URL}`."
                ),
            )
        if api_key is None and os.getenv("ARGILLA_API_KEY") is None:
            warnings.warn(
                (
                    "Since `api_key` is None, and the env var `ARGILLA_API_KEY` is not"
                    f" set, it will default to `{self.DEFAULT_API_KEY}`."
                ),
            )

        # Connect to Argilla with the provided credentials, if applicable
        try:
            rg.init(api_key=api_key, api_url=api_url)
        except Exception as e:
            raise ConnectionError(
                f"Could not connect to Argilla with exception: '{e}'.\n"
                "Please check your `api_key` and `api_url`, and make sure that "
                "the Argilla server is up and running. If the problem persists "
                f"please report it to {self.ISSUES_URL} as an `integration` issue."
            ) from e

        # Set the Argilla variables
        self.dataset_name = dataset_name
        self.workspace_name = workspace_name or rg.get_workspace()
        self.feedback_dataset = feedback_dataset or FeedbackDataset(
            fields=[
                rg.TextField(name="step"),
                rg.TextField(name="prompt"),
                rg.TextField(name="response"),
            ],
            questions=[
                rg.RatingQuestion(
                    name="response_rating",
                    title="Rate the response",
                    values=[1, 2, 3, 4, 5],
                    description="1: Awful, 5: Excellent",
                ),
                rg.TextQuestion(name="improved_response", title="Provide a better response to the prompt"),
            ],
        )
        self.generation_kwargs = generation_kwargs or {"max_new_tokens": 128}

        if not ({"prompt", "response"} <= {field.name for field in self.feedback_dataset.fields}):
            raise ValueError(
                f"The provided `FeedbackDataset` must have `TextField` instances with `prompt` and `response` as names."
            )

    # def on_init_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
    #     return super().on_init_end(args, state, control, **kwargs)

    # def on_log(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
    #     logs = kwargs.pop("logs", None)
    #     breakpoint()
    #     return super().on_log(args, state, control, **kwargs)

    def on_evaluate(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        if not ({"model", "tokenizer", "eval_dataloader"} <= set(kwargs)):
            return
        model = kwargs.get("model")
        tokenizer = kwargs.get("tokenizer")
        eval_dataloader = kwargs.get("eval_dataloader")
        # Set the padding side to the left for generation
        original_padding_side = tokenizer.padding_side
        tokenizer.padding_side = "left"
        # eval_size = len(eval_dataloader.dataset)
        # inputs = eval_dataloader.dataset.select(range(min(args.per_device_eval_batch_size, eval_size)))
        # assert set(inputs.column_names) == {"input_ids", "attention_mask"}
        # breakpoint()
        # # input_dict = {key: torch.tensor(value, device=torch.device(model.device)) for key, value in inputs.to_dict().items()}
        # max_length = max([len(ids) for ids in inputs["input_ids"]])
        # inputs = {
        #     "input_ids": F.pad(inputs["input_ids"], (0, max_length - )
        #     "attention_mask"
        # }
        # Extract the padded samples
        inputs = next(iter(eval_dataloader))
        # inputs.pop("labels", None)
        inputs.to(model.device)

        # Reset the padding side
        tokenizer.padding_side = original_padding_side

        with torch.no_grad():
            breakpoint()
            outputs = model.generate(**inputs, **self.generation_kwargs)
            input_text = tokenizer.batch_decode(inputs["input_ids"], skip_special_tokens=True)
            tokenized = tokenizer.batch_decode(outputs, skip_special_tokens=True)
            print(tokenized)
