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

from social_core.backends.github import GithubOAuth2

from argilla_server.security.authentication.claims import Claims
from argilla_server.security.authentication.oauth2.providers._base import OAuth2ClientProvider


class GitHubClientProvider(OAuth2ClientProvider):
    claims = Claims(
        picture="avatar_url",
        identity=lambda user: f"{user.provider}:{user.id}",
        username="login",
    )
    backend_class = GithubOAuth2
    name = "github"
