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

import os
import sqlite3
import time
from urllib.parse import urlparse
from pathlib import Path

from argilla_server.database import database_url_sync

url_db = database_url_sync()
db_path = Path(urlparse(url_db).path)

backup_path = Path("/data/argilla/backup")

if not backup_path.exists():
    backup_path.mkdir()

while True:
    with sqlite3.connect(db_path, isolation_level="DEFERRED") as conn:
        backup_file = os.path.join(backup_path.absolute(), db_path.name)

        os.system(f"cp {db_path.absolute()} {backup_file}")
        os.system(f"cp {db_path.absolute()}-wal {backup_file}-wal")

    time.sleep(15)
