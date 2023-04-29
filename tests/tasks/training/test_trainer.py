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


# TODO: extend testing suite https://github.com/pytest-dev/pytest/issues/3344
# @pytest.mark.parametrize("framework", [("spacy", "en_core_web_sm", "max_steps"), ("setfit", "all-MiniLM-L6-v2", "num_iterations"), ("transformers", "prajjwal1/bert-tiny", "max_steps")])
# def test_train_spacy(cli_runner: CliRunner, cli: Typer, dataset_text_classification: str, framework: str):
#     result = cli_runner.invoke(
#         cli,
#         f"train --name '{dataset_text_classification}' --framework '{framework[0]}' --output-dir '' --model '{framework[1]}' --update-config-kwargs '{{\"{framework[2]}\": 1}}'",
#     )
#     assert result.exit_code == 0
