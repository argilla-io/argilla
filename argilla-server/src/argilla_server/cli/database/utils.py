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

import io

from alembic import command
from alembic.config import Config


def get_current_revision(alembic_config_file: str, verbose: bool = False) -> str:
    output_buffer = io.StringIO()
    alembic_cfg = Config(alembic_config_file, stdout=output_buffer)

    command.current(alembic_cfg, verbose=verbose)
    command_result = output_buffer.getvalue().strip()

    if verbose:
        return command_result
    return command_result.split(" ")[0]
