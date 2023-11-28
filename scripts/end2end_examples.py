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
To run this script you need to install papermill first:

$ pip install papermill

Then run the script from the argilla repo root:

$ cd argilla-repo
$ python scripts/end2end_examples.py --help
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import papermill
import typer
from argilla._constants import DEFAULT_API_KEY


@dataclass
class ExampleNotebook:
    sort_index: int = field(init=False)
    src_filename: Path
    dst_filename: Path
    parameters: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.src_filename = Path(self.src_filename)
        assert self.src_filename.exists(), f"File {self.src_filename} does not exist"
        self.sort_index = int(self.src_filename.stem.split("-")[-1])
        self.dst_filename = Path(self.dst_filename)
        dst_folder = self.dst_filename.parent
        if not dst_folder.exists():
            dst_folder.mkdir(exist_ok=True)

    def run(self):
        try:
            papermill.execute_notebook(
                str(self.src_filename),
                str(self.dst_filename),
                parameters=self.parameters,
                kernel_name="python3",
            )
            print(f"✅  {self.src_filename}")
        except Exception as e:
            print(f"❌  {self.src_filename}")
            raise e from None

    def clean(self):
        if self.dst_filename.exists():
            self.dst_filename.unlink()
            print(f"Removed output notebook: {self.dst_filename.stem}")


def get_huggingface_token() -> Optional[str]:
    if token := os.environ.get("HF_HUB_ACCESS_TOKEN"):
        return token

    from huggingface_hub import HfFolder

    if token := HfFolder.get_token():
        return token

    raise ValueError("No token found. Please set HF_HUB_ACCESS_TOKEN environment variable.")


def main(
    api_url: Optional[str] = "http://localhost:6900",
    api_key: Optional[str] = DEFAULT_API_KEY,
    hf_token: Optional[str] = None,
    examples_folder: Optional[Path] = "docs/_source/tutorials_and_integrations/tutorials/feedback/end2end_examples",
) -> None:
    """
    Run the end2end example notebooks. If no arguments are passed, it
    will try to get the api_key and the hf_token from the environment variables.
    """
    if not hf_token:
        hf_token = get_huggingface_token()

    notebook_parameters = {
        "hf_token": hf_token,
        "api_url": api_url,
        "api_key": api_key,
    }

    # Name of the output notebook that will be removed after running the examples
    output_notebook = "output_notebook.ipynb"

    output_folder = examples_folder.parent / "end2end_outputs"

    examples = []
    for filename in examples_folder.glob("*.ipynb"):
        examples.append(
            ExampleNotebook(
                src_filename=filename,
                dst_filename=output_folder / output_notebook,
                parameters=notebook_parameters,
            )
        )
    examples = sorted(examples, key=lambda x: x.sort_index)

    for example in examples:
        example.run()
        example.clean()

    if output_folder.exists():
        output_folder.rmdir()
        print(f"Removed output folder: {output_folder.name}")


if __name__ == "__main__":
    typer.run(main)
