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

import pytest

from argilla_server.errors.future import NotFoundError
from argilla_server.security.authentication.oauth2 import OAuth2Settings


class TestOAuth2Settings:
    def test_configure_unsupported_provider(self):
        with pytest.raises(NotFoundError):
            OAuth2Settings.from_dict({"providers": [{"name": "unsupported"}]})

    def test_configure_github_provider(self):
        settings = OAuth2Settings.from_dict(
            {
                "providers": [
                    {
                        "name": "github",
                        "client_id": "github_client_id",
                        "client_secret": "github_client_secret",
                        "scope": "user:email",
                    }
                ]
            }
        )
        github_provider = settings.providers["github"]

        assert github_provider.name == "github"
        assert github_provider.client_id == "github_client_id"
        assert github_provider.client_secret == "github_client_secret"
        assert github_provider.scope == ["user:email"]

    def test_configure_huggingface_provider(self):
        settings = OAuth2Settings.from_dict(
            {
                "providers": [
                    {
                        "name": "huggingface",
                        "client_id": "huggingface_client_id",
                        "client_secret": "huggingface_client_secret",
                        "scope": "openid profile email",
                    }
                ]
            }
        )
        huggingface_provider = settings.providers["huggingface"]

        assert huggingface_provider.name == "huggingface"
        assert huggingface_provider.client_id == "huggingface_client_id"
        assert huggingface_provider.client_secret == "huggingface_client_secret"
        assert huggingface_provider.scope == ["openid", "profile", "email"]
