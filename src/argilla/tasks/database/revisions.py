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
from typing import Optional

import typer

from argilla.server.database import TAGGED_REVISIONS, revisions


def revisions_cmd():
    typer.echo("\n\nTagged revisions:\n")
    for version, revision in TAGGED_REVISIONS.items():
        typer.echo(f"• {version} ({revision!r})")
    typer.echo("\n\nAlembic revisions:\n")
    revisions()


if __name__ == "__main__":
    typer.run(revisions_cmd)
