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

import json
import os

import argilla as rg
import click
from argilla.training import ArgillaTrainer


@click.command()
@click.option("-n", "--name", help="The name of the dataset to be used for training.")
@click.option("-f", "--framework", help="Choose a framework: transformers, openai, span_marker, setfit or spacy.")
@click.option("-w", "--workspace", help="The workspace to be used for training.")
@click.option("-l", "--limit", default=None, help="The number of record to be used.")
@click.option("-q", "--query", default=None, help="The query to be used.")
@click.option("-m", "--model", default=None, help="The modelname or path to be used for training.")
@click.option("-t", "--train-size", default=1.0, help="The train split to be used.")
@click.option("-s", "--seed", default=42, help="The random seed number.")
@click.option("-d", "--device", default=-1, help="The GPU id to be used for training.")
@click.option("-o", "--output-dir", default="model", help="Output directory for the saved model.")
@click.option(
    "--update-config-kwargs", default={}, help="update_config() kwargs to be passed as JSON-serializable string."
)
@click.option("--api-url", default=os.environ.get("ARGILLA_API_URL"), help="Api url to be used for training.")
@click.option("--api-key", default=os.environ.get("ARGILLA_API_KEY"), help="Api key to be used for training.")
def train(
    name: str,
    framework: str,
    workspace: str,
    limit: int,
    query: str,
    model: str,
    train_size: float,
    seed: int,
    device: int,
    output_dir: str,
    update_config_kwargs: dict,
    api_url: str,
    api_key: str,
):
    """Creates a default training task using CLI commands."""
    rg.init(api_url=api_url, api_key=api_key)
    trainer = ArgillaTrainer(
        name=name,
        framework=framework,
        workspace=workspace,
        model=model,
        train_size=train_size,
        seed=seed,
        gpu_id=device,
        limit=limit,
        query=query,
    )
    trainer.update_config(**json.loads(update_config_kwargs))
    trainer.train(output_dir=output_dir)


if __name__ == "__main__":
    train()
