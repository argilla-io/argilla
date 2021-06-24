import os
import warnings
from enum import Enum
from typing import Optional

from pydantic import BaseSettings, Field, root_validator


class AuthProviderType(str, Enum):
    local = "local"


# TODO(frascuchon): Merge with common ApiSettings
class SecuritySettings(BaseSettings):
    """
    Api security settings

    enable_security:
        If True, enables api security mechanisms. Default=False

    auth_provider:
        The auth provider used for api authentication (if provided).
        No auth mechanisms will be used if no provided
        (same as ENABLE_SECURITY=False)
    """

    enable_security: bool = False
    auth_provider: Optional[str] = Field(default=None)

    @root_validator
    def check_settings(cls, values):

        if "ENABLE_SECURITY" in os.environ:
            warnings.warn(
                "ENABLE_SECURITY environment variable is deprecated and"
                " will removed in version 0.2.0 "
                "Use RUBRIX_AUTH_PROVIDER instead with allowed values: "
                "['local']"
            )
            enable_security = values["enable_security"]
            if enable_security:
                values["auth_provider"] = "local"

        auth_provider = values.get("auth_provider", None)
        values["enable_security"] = auth_provider is not None
        return values

    class Config:
        env_prefix = "RUBRIX_"
        fields = {
            "enable_security": {
                "env": "ENABLE_SECURITY",
            }
        }


settings = SecuritySettings()
