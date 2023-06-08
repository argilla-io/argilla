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

from pathlib import Path

from huggingface_hub import DatasetCard

TEMPLATE_ARGILLA_DATASET_CARD_PATH = Path(__file__).parent / "argilla_template.md"


class ArgillaDatasetCard(DatasetCard):
    """`ArgillaDatasetCard` has been created similarly to `DatasetCard` from
    `huggingface_hub` but with a different template. The template is located at
    `argilla/client/feedback/card/argilla_template.md`.
    """

    default_template_path = TEMPLATE_ARGILLA_DATASET_CARD_PATH
