"""
Snapshots environment vars / settings
"""

from pydantic import BaseSettings


class SnapshotSettings(BaseSettings):
    """
    Snapshot environment variables settings

    snapshots_provider:
        The snapshot provider

    """

    snapshots_provider: str = "local"
    snapshots_path: str = ".snapshots"


settings = SnapshotSettings()
