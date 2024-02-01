import os

import psutil


def is_quickstart_server():
    """Returns True if the current process is running on the Quickstart server, False otherwise."""
    global _is_quickstart_server

    if _is_quickstart_server is None:
        _is_quickstart_server = is_running_on_docker_container() and _is_quickstart_env()
    return _is_quickstart_server


def is_running_on_docker_container():
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
_is_quickstart_server = None
