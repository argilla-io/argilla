#  coding=utf-8
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
from .auth_provider import DBAuthProvider
from .auth_provider.base import AuthProvider, api_key_header

from argilla.server.security.auth_provider import AuthProvider, DBAuthProvider, OAuth2Provider, api_key_header
from argilla.server.settings import settings

if settings.oauth_enabled:
    auth = OAuth2Provider.new_instance()
else:
    auth = DBAuthProvider.new_instance()
