from pydantic import BaseSettings

_DEFAULT_API_KEY = "argilla.apikey"
_DEFAULT_API_URL = "https://localhost:6900"


class HTTPClientConfig(BaseSettings):
    api_url: str = _DEFAULT_API_URL
    api_key: str = _DEFAULT_API_KEY

    class Config:
        env_prefix = "ARGILLA_"
