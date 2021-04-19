"""
Snapshots environment vars / settings
"""
from typing import Optional

from pydantic import BaseSettings, root_validator


class SnapshotSettings(BaseSettings):
    """
    Snapshot environment variables settings

    snapshots_provider:
        The snapshot provider. Options are: "local", "s3". Default="local"
    snapshots_path:
        The file system path where snapshots will be created whe provider is set to "local".
        Default=".snapshots"
    snapshots_s3_bucket:
        The s3 bucket used for store and retrieve snapshots when provider is set to "s3".
        Provided bucket must exists

    """

    snapshots_provider: str = "local"
    snapshots_path: str = ".snapshots"
    snapshots_s3_bucket: Optional[str] = None

    @root_validator
    def check_configuration(cls, values):
        provider = values["snapshots_provider"]

        if provider == "s3":
            s3_bucket = values.get("snapshots_s3_bucket")
            assert s3_bucket, (
                "s3 provider was set but no bucket info was provided. "
                "Please define SNAPSHOTS_S3_BUCKET env var if you want to configure s3 snapshots backend"
            )
        return values


settings = SnapshotSettings()
