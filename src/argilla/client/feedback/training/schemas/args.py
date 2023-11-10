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

from pydantic import BaseModel

if TYPE_CHECKING:
    import sentence_transformers


class Model(BaseModel):
    name: str


class _OpenAITrainingArgsHyperParameters(Model):
    n_epochs: int = 1


class OpenAITrainingArgs(BaseModel):
    hyperparameters: _OpenAITrainingArgsHyperParameters = _OpenAITrainingArgsHyperParameters()


class TransformersModelArgs(Model):
    pass


class TransformersTrainerArgs(Model):
    pass


class PeftLoraArgs(BaseModel):
    r: int = 8
    target_modules: str = None
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    fan_in_fan_out: bool = False
    bias: str = "none"
    inference_mode: bool = False
    modules_to_save: str = None
    init_lora_weights: bool = True


class SetFitModelArgs(BaseModel):
    pretrained_model_name_or_path: str = None
    revision: str = None
    force_download: bool = False
    resume_download: bool = False
    proxies: dict = None
    token: str = None
    cache_dir: str = None
    local_files_only: bool = False
    model_kwargs: dict = None


"""Trainer to train a SetFit model.

    Args:
        model (`SetFitModel`, *optional*):
            The model to train. If not provided, a `model_init` must be passed.
        train_dataset (`Dataset`):
            The training dataset.
        eval_dataset (`Dataset`, *optional*):
            The evaluation dataset.
        model_init (`Callable[[], SetFitModel]`, *optional*):
            A function that instantiates the model to be used. If provided, each call to [`~SetFitTrainer.train`] will start
            from a new instance of the model as given by this function when a `trial` is passed.
        metric (`str` or `Callable`, *optional*, defaults to `"accuracy"`):
            The metric to use for evaluation. If a string is provided, we treat it as the metric name and load it with default settings.
            If a callable is provided, it must take two arguments (`y_pred`, `y_test`).
        metric_kwargs (`Dict[str, Any]`, *optional*):
            Keyword arguments passed to the evaluation function if `metric` is an evaluation string like "f1".
            For example useful for providing an averaging strategy for computing f1 in a multi-label setting.
        loss_class (`nn.Module`, *optional*, defaults to `CosineSimilarityLoss`):
            The loss function to use for contrastive training.
        num_iterations (`int`, *optional*, defaults to `20`):
            The number of iterations to generate sentence pairs for.
            This argument is ignored if triplet loss is used.
            It is only used in conjunction with `CosineSimilarityLoss`.
        num_epochs (`int`, *optional*, defaults to `1`):
            The number of epochs to train the Sentence Transformer body for.
        learning_rate (`float`, *optional*, defaults to `2e-5`):
            The learning rate to use for contrastive training.
        batch_size (`int`, *optional*, defaults to `16`):
            The batch size to use for contrastive training.
        seed (`int`, *optional*, defaults to 42):
            Random seed that will be set at the beginning of training. To ensure reproducibility across runs, use the
            [`~SetTrainer.model_init`] function to instantiate the model if it has some randomly initialized parameters.
        column_mapping (`Dict[str, str]`, *optional*):
            A mapping from the column names in the dataset to the column names expected by the model. The expected format is a dictionary with the following format: {"text_column_name": "text", "label_column_name: "label"}.
        use_amp (`bool`, *optional*, defaults to `False`):
            Use Automatic Mixed Precision (AMP). Only for Pytorch >= 1.6.0
        warmup_proportion (`float`, *optional*, defaults to `0.1`):
            Proportion of the warmup in the total training steps.
            Must be greater than or equal to 0.0 and less than or equal to 1.0.
        distance_metric (`Callable`, defaults to `BatchHardTripletLossDistanceFunction.cosine_distance`):
            Function that returns a distance between two embeddings.
            It is set for the triplet loss and
            is ignored for `CosineSimilarityLoss` and `SupConLoss`.
        margin (`float`, defaults to `0.25`): Margin for the triplet loss.
            Negative samples should be at least margin further apart from the anchor than the positive.
            This is ignored for `CosineSimilarityLoss`, `BatchHardSoftMarginTripletLoss` and `SupConLoss`.
        samples_per_label (`int`, defaults to `2`): Number of consecutive, random and unique samples drawn per label.
            This is only relevant for triplet loss and ignored for `CosineSimilarityLoss`.
            Batch size should be a multiple of samples_per_label.
    """


class SetFitTrainerArgs(BaseModel):
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


class SpacyTrainerArgs(BaseModel):
    pass
