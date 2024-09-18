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

import alembic.config
import typer

from argilla_server.database import ALEMBIC_CONFIG_FILE, TAGGED_REVISIONS

from . import utils


def revisions():
    current_revision = utils.get_current_revision(ALEMBIC_CONFIG_FILE, verbose=True)

    typer.echo("")
    typer.echo("Tagged revisions")
    typer.echo("-----------------")
    for version, revision in TAGGED_REVISIONS.items():
        typer.echo(f"• {version} (revision: {revision!r})")

    typer.echo("")
    typer.echo("Alembic revisions")
    typer.echo("-----------------")
    alembic.config.main(argv=["-c", ALEMBIC_CONFIG_FILE, "history"])

    typer.echo("")
    typer.echo("Current revision")
    typer.echo("----------------")
    typer.echo(current_revision)


if __name__ == "__main__":
    typer.run(revisions)
