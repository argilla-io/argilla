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

"""
To run this script you need to install papermill apart from argilla:

$ pip install papermill

Then run the script:

$ python scripts/end2end_examples.py --help
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import papermill
import typer

EXAMPLES_FOLDER = Path(__file__).parent.parent / "docs/_source/practical_guides/examples/text_classification"
OUTPUT_FOLDER = EXAMPLES_FOLDER / "output_notebooks"


@dataclass
class ExampleNotebook:
    src_filename: Path
    dst_filename: Path
    parameters: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.src_filename = EXAMPLES_FOLDER / self.src_filename
        assert self.src_filename.exists(), f"File {self.src_filename} does not exist"
        dst_folder = OUTPUT_FOLDER
        if not dst_folder.exists():
            dst_folder.mkdir(exist_ok=True)
        self.dst_filename = dst_folder / self.dst_filename

    def run(self):
        try:
            papermill.execute_notebook(str(self.src_filename), str(self.dst_filename), parameters=self.parameters)
            print(f"✅  {self.src_filename.stem}")
        except Exception as e:
            print(f"❌  {self.src_filename.stem}")
            raise e from None

    def clean(self):
        if self.dst_filename.exists():
            self.dst_filename.unlink()
            print(f"Removed output notebook: {self.dst_filename.stem}")


def get_argilla_api_key() -> Optional[str]:
    if api_key := os.environ.get("ADMIN_API_KEY"):
        # Try to grab the api_key from the environment variable set in quickstart.Dockerfile
        return api_key

    from argilla.client.login import ArgillaCredentials

    if ArgillaCredentials.exists():
        credentials = ArgillaCredentials.load()
        return credentials.api_key

    raise ValueError("No api_key found. Please set ADMIN_API_KEY environment variable.")


def get_huggingface_token() -> Optional[str]:
    if token := os.environ.get("HF_HUB_ACCESS_TOKEN"):
        return token

    from huggingface_hub import HfFolder

    if token := HfFolder.get_token():
        return token

    raise ValueError("No token found. Please set HF_HUB_ACCESS_TOKEN environment variable.")


def main(api_url: str = "http://localhost:6900", api_key: Optional[str] = None, hf_token: Optional[str] = None) -> None:
    """
    Run the end2end example notebooks. If no arguments are passed, it
    will try to get the api_key and the hf_token from the environment variables.
    """
    if not api_key:
        api_key = get_argilla_api_key()
    if not hf_token:
        hf_token = get_huggingface_token()

    notebook_parameters = {
        "api_url": api_url,
        "api_key": api_key,
        "hf_token": hf_token,
    }

    examples = [
        ExampleNotebook(
            src_filename="text-classification-create-dataset.ipynb",
            dst_filename="output-notebook.ipynb",
            parameters=notebook_parameters,
        ),
    ]
    for example in examples:
        example.run()
        example.clean()

    if OUTPUT_FOLDER.exists():
        OUTPUT_FOLDER.rmdir()
        print(f"Removed output folder: {OUTPUT_FOLDER.name}")


if __name__ == "__main__":
    typer.run(main)
