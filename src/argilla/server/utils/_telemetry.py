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

import psutil


def server_deployment_type() -> str:
    """Returns the type of deployment of the server."""
    global _server_deployment_type

    if _server_deployment_type is None:
        _server_deployment_type = "server"

        if is_running_on_docker_container() and _is_quickstart_env():
            _server_deployment_type = "quickstart"

    return _server_deployment_type


def is_running_on_docker_container() -> bool:
    """Returns True if the current process is running inside a Docker container, False otherwise."""
    global _in_docker_container

    if _in_docker_container is None:
        _in_docker_container = _has_docker_env() or _has_docker_cgroup()

    return _in_docker_container


def _has_docker_env() -> bool:
    try:
        return os.path.exists("/.dockerenv")
    except:
        return False


def _has_docker_cgroup() -> bool:
    try:
        cgroup_path = "/proc/self/cgroup"
        return (
            os.path.exists(cgroup_path)
            and os.path.isfile(cgroup_path)
            and any("docker" in line for line in open(cgroup_path))
        )
    except:
        return False


def _is_quickstart_script_running() -> bool:
    # TODO: Any modification in the `quickstart.Dockerfile` file should be reflected here

    try:
        cmdline_key = "cmdline"
        for process in psutil.process_iter([cmdline_key]):
            if "start_quickstart_argilla.sh" in process.info[cmdline_key]:
                return True
    except:
        pass
    return False


def _is_quickstart_env():
    # TODO: Any modification in the `quickstart.Dockerfile` file should be reflected here

    for env_var in [
        "OWNER_USERNAME",
        "OWNER_PASSWORD",
        "OWNER_API_KEY",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD",
        "ADMIN_API_KEY",
        "ANNOTATOR_USERNAME",
        "ANNOTATOR_PASSWORD",
        "LOAD_DATASETS",
    ]:
        if env_var not in os.environ:
            return False
    return True


# Private global variables section
_in_docker_container = None
_server_deployment_type = None
