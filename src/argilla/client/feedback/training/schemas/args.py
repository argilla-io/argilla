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

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    import sentence_transformers


class PydanticConfig(BaseModel):
    model_config = ConfigDict(extra="allow")


class Model(PydanticConfig):
    name: str


class _OpenAITrainingArgsHyperParameters(Model):
    n_epochs: int = 1


class OpenAITrainingArgs(PydanticConfig):
    hyperparameters: _OpenAITrainingArgsHyperParameters = _OpenAITrainingArgsHyperParameters()


class TransformersModelArgs(PydanticConfig):
    pretrained_model_name_or_path: str = None
    force_download: bool = False
    resume_download: bool = False
    proxies: dict = None
    token: str = None
    cache_dir: str = None
    local_files_only: bool = False


class TransformersTrainerArgs(PydanticConfig):
    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 8
    gradient_accumulation_steps: int = 1
    learning_rate: float = 5e-5
    weight_decay: float = 0
    adam_beta1: float = 0.9
    adam_beta2: float = 0.9
    adam_epsilon: float = 1e-8
    max_grad_norm: float = 1
    learning_rate: float = 5e-5
    num_train_epochs: int = 3
    max_steps: int = 0
    log_level: str = "passive"
    logging_strategy: str = "steps"
    save_strategy: str = "steps"
    save_steps: int = 500
    seed: int = 42
    push_to_hub: bool = False
    hub_model_id: str = "user_name/output_dir_name"
    hub_strategy: str = "every_save"
    hub_token: str = "1234"
    hub_private_repo: bool = False


class PeftLoraArgs(PydanticConfig):
    r: int = 8
    target_modules: str = None
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    fan_in_fan_out: bool = False
    bias: str = "none"
    inference_mode: bool = False
    modules_to_save: str = None
    init_lora_weights: bool = True


class SetFitModelArgs(PydanticConfig):
    pretrained_model_name_or_path: str = None
    force_download: bool = False
    resume_download: bool = False
    proxies: dict = None
    token: str = None
    cache_dir: str = None
    local_files_only: bool = False
    model_kwargs: dict = None


class SetFitTrainerArgs(PydanticConfig):
    model: SetFitModelArgs = None
    train_dataset: str = None
    eval_dataset: str = None
    model_init: str = None
    metric: str = "accuracy"
    metric_kwargs: dict = None
    loss_class: "sentence_transformers.losses" = None
    num_iterations: int = 20
    num_epochs: int = 1
    learning_rate: float = 2e-5
    batch_size: int = 16
    seed: int = 42
    column_mapping: dict = None
    use_amp: bool = False
    warmup_proportion: float = 0.1
    distance_metric: "sentence_transformers.losses" = None
    margin: float = 0.25
    samples_per_label: int = 2


class SpacyTrainerArgs(PydanticConfig):
    pass
