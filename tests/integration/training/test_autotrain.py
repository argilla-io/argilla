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

# import os

# import pytest
# from argilla.training import ArgillaTrainer

# FRAMEWORK = "autotrain"
# MODELS = ["prajjwal1/bert-tiny", "autotrain"]
# _HF_HUB_ACCESS_TOKEN = os.environ.get("HF_AUTH_TOKEN") or os.environ.get("HF_HUB_ACCESS_TOKEN")


# @pytest.mark.skipif(
#     _HF_HUB_ACCESS_TOKEN is None,
#     reason="You need a HF Hub access token to test the push_to_hub feature",
# )
# @pytest.mark.parametrize("model", MODELS)
# def test_update_config(dataset_text_classification, model):
#     trainer = ArgillaTrainer(
#         name=dataset_text_classification, model=model, train_size=0.8, limit=10, framework=FRAMEWORK
#     )
#     trainer.update_config(autotrain=[{"num_models": 1}])
#     assert trainer._trainer.trainer_kwargs["autotrain"][0]["num_models"] == 1
#     trainer.update_config(hub_model=[{"epochs": 1}])
#     assert trainer._trainer.trainer_kwargs["hub_model"][0]["epochs"] == 1
#     trainer.train()


# @pytest.mark.skipif(
#     _HF_HUB_ACCESS_TOKEN is None,
#     reason="You need a HF Hub access token to test the push_to_hub feature",
# )
# @pytest.mark.parametrize("model", MODELS)
# def test_passed_functions(dataset_text_classification, model):
#     trainer = ArgillaTrainer(name=dataset_text_classification, model=model, limit=10, framework=FRAMEWORK)
#     trainer._trainer.init_model()
#     trainer._trainer.init_pipeline()
#     trainer._trainer.predict("useless")
#     trainer._trainer.save(output_dir="useless")


# @pytest.mark.skipif(
#     _HF_HUB_ACCESS_TOKEN is None,
#     reason="You need a HF Hub access token to test the push_to_hub feature",
# )
# def test_autotrain_train_multi_label(dataset_text_classification_multi_label):
#     with pytest.raises(NotImplementedError):
#         ArgillaTrainer(name=dataset_text_classification_multi_label, model=MODELS[0], limit=10, framework=FRAMEWORK)


# @pytest.mark.skipif(
#     _HF_HUB_ACCESS_TOKEN is None,
#     reason="You need a HF Hub access token to test the push_to_hub feature",
# )
# def test_autotrain_train_token(dataset_token_classification):
#     with pytest.raises(NotImplementedError):
#         ArgillaTrainer(name=dataset_token_classification, model=MODELS[0], limit=10, framework=FRAMEWORK)


# @pytest.mark.skipif(
#     _HF_HUB_ACCESS_TOKEN is None,
#     reason="You need a HF Hub access token to test the push_to_hub feature",
# )
# def test_autotrain_train_text2text(dataset_text2text):
#     with pytest.raises(NotImplementedError):
#         ArgillaTrainer(name=dataset_text2text, model=MODELS[0], limit=10, framework=FRAMEWORK)
