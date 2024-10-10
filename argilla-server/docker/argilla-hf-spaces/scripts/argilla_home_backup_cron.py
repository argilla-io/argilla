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

import httpx

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


def _run_backup(src: Path, dst_folder: Path, backup_id: int):
    backup_folder = Path(dst_folder) / str(backup_id)

    # Creating a copy of existing backup
    backup_folder.mkdir(exist_ok=True)

    backup_file = os.path.join(backup_folder, src.name)

    src_conn = sqlite3.connect(src, isolation_level="DEFERRED")
    dst_conn = sqlite3.connect(backup_file, isolation_level="DEFERRED")

    try:
        _LOGGER.info("Creating a db backup in %s", backup_file)
        with src_conn, dst_conn:
            src_conn.backup(dst_conn)
        _LOGGER.info("DB backup created at %s", backup_file)
    finally:
        src_conn.close()
        dst_conn.close()


def db_backup(backup_folder: str, interval: int = 15, num_of_backups: int = 20):
    url_db = database_url_sync()
    db_path = Path(urlparse(url_db).path)

    backup_path = Path(backup_folder).absolute()

    if not backup_path.exists():
        backup_path.mkdir()

    backup_id = 0
    while True:
        try:
            _run_backup(src=db_path, dst_folder=backup_path, backup_id=backup_id)
            backup_id = (backup_id + 1) % num_of_backups
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


def is_argilla_alive():
    try:
        with httpx.Client() as client:
            response = client.get("http://localhost:6900/api/v1/status")
            response.raise_for_status()
        return True
    except Exception as e:
        _LOGGER.exception(f"Error checking if argilla is alive: {e}")
        return False


if __name__ == "__main__":
    argilla_data: str = "/data/argilla"
    backup_path = os.environ["ARGILLA_BACKUP_PATH"]
    backup_interval = int(os.getenv("ARGILLA_BACKUP_INTERVAL") or "15")
    num_of_backups = int(os.getenv("ARGILLA_NUM_OF_BACKUPS") or "20")

    while not is_argilla_alive():
        _LOGGER.info("Waiting for the server to be ready...")
        time.sleep(5)

    server_id_backup(argilla_data)
    db_backup(backup_path, interval=backup_interval, num_of_backups=num_of_backups)
