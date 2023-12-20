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

import typer

from argilla.client.models import Framework

app = typer.Typer(no_args_is_help=True)


def framework_callback(value: str):
    try:
        return Framework(value.lower())
    except ValueError:
        raise typer.BadParameter(f"Invalid framework {value}. Choose from {', '.join([f.value for f in Framework])}")


# using callback to ensure it is used as sole command
@app.callback(help="Starts the ArgillaTrainer", invoke_without_command=True)
def train(
    name: str = typer.Option(default=None, help="The name of the dataset to be used for training."),
    framework: Framework = typer.Option(default=None, help="The framework to be used for training."),
    workspace: str = typer.Option(default=None, help="The workspace to be used for training."),
    limit: int = typer.Option(default=None, help="The number of record to be used."),
    query: str = typer.Option(default=None, help="The query to be used."),
    model: str = typer.Option(default=None, help="The modelname or path to be used for training."),
    train_size: float = typer.Option(default=1.0, help="The train split to be used."),
    seed: int = typer.Option(default=42, help="The random seed number."),
    device: int = typer.Option(default=-1, help="The GPU id to be used for training."),
    output_dir: str = typer.Option(default="model", help="Output directory for the saved model."),
    update_config_kwargs: str = typer.Option(default={}, help="update_config() kwargs to be passed as a dictionary."),
):
    import json

    from argilla.cli.callback import init_callback
    from argilla.client.singleton import init
    from argilla.training import ArgillaTrainer

    init_callback()

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
    if output_dir:
        trainer.train(output_dir=output_dir)
    else:
        trainer.train()


if __name__ == "__main__":
    app()
