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
import logging
import os
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlparse

from argilla_server.database import database_url_sync
from argilla_server.settings import settings
from argilla_server.telemetry import get_server_id, SERVER_ID_DAT_FILE

logging.basicConfig(
    handlers=[logging.StreamHandler()],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    force=True,
)

_LOGGER = logging.getLogger("argilla.backup")


def _run_backup(src: Path, dst_folder: str):
    bak_folder = Path(dst_folder) / "bak"

    # Creating a copy of existing backup
    os.system(f"rm -rf {bak_folder}/")
    bak_folder.mkdir(exist_ok=True)
    os.system(f"mv {os.path.join(dst_folder, src.name)}* {bak_folder}/")

    backup_file = os.path.join(dst_folder, src.name)

    src_conn = sqlite3.connect(src, isolation_level="DEFERRED")
    dst_conn = sqlite3.connect(backup_file, isolation_level="DEFERRED")

    try:
        _LOGGER.info("Creating a db backup...")
        with src_conn, dst_conn:
            src_conn.backup(dst_conn)
        _LOGGER.info("DB backup created!")
    finally:
        src_conn.close()
        dst_conn.close()


def db_backup(backup_folder: str, interval: int = 15):
    url_db = database_url_sync()
    db_path = Path(urlparse(url_db).path)

    backup_path = Path(backup_folder).absolute()

    if not backup_path.exists():
        backup_path.mkdir()

    while True:
        try:
            _run_backup(src=db_path, dst_folder=backup_path)
        except Exception as e:
            _LOGGER.exception(f"Error creating backup: {e}")

        time.sleep(interval)


def server_id_backup(backup_folder: str):
    backup_path = Path(backup_folder).absolute()
    if not backup_path.exists():
        backup_path.mkdir()

    # Force to create the server id file
    get_server_id()

    server_id_file = os.path.join(settings.home_path, SERVER_ID_DAT_FILE)

    _LOGGER.info(f"Copying server id file to {backup_folder}")
    os.system(f"cp {server_id_file} {backup_folder}")
    _LOGGER.info("Server id file copied!")


if __name__ == "__main__":
    backup_folder: str = "./data/argilla/backup"

    backup_interval = int(os.getenv("ARGILLA_BACKUP_INTERVAL") or "15")

    server_id_backup(backup_folder)
    db_backup(backup_folder, interval=backup_interval)
