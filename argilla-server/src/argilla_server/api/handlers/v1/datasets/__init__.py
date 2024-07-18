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

from fastapi import APIRouter

from argilla_server.api.handlers.v1.datasets.datasets import router as datasets_router
from argilla_server.api.handlers.v1.datasets.questions import router as questions_router
from argilla_server.api.handlers.v1.datasets.records import router as records_router
from argilla_server.api.handlers.v1.datasets.records_bulk import router as records_bulk_router

router = APIRouter(tags=["datasets"])

router.include_router(datasets_router)
router.include_router(questions_router)
router.include_router(records_router)
router.include_router(records_bulk_router)
