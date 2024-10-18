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

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from rq.job import Job
from rq.exceptions import NoSuchJobError

from argilla_server.database import get_async_db
from argilla_server.jobs.queues import REDIS_CONNECTION
from argilla_server.models import User
from argilla_server.api.policies.v1 import JobPolicy, authorize
from argilla_server.api.schemas.v1.jobs import Job as JobSchema
from argilla_server.security import auth

router = APIRouter(tags=["jobs"])


def _get_job(job_id: str) -> Job:
    try:
        return Job.fetch(job_id, connection=REDIS_CONNECTION)
    except NoSuchJobError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id `{job_id}` not found",
        )


@router.get("/jobs/{job_id}", response_model=JobSchema)
async def get_job(
    *,
    db: AsyncSession = Depends(get_async_db),
    job_id: str,
    current_user: User = Security(auth.get_current_user),
):
    job = _get_job(job_id)

    await authorize(current_user, JobPolicy.get)

    return JobSchema(id=job.id, status=job.get_status(refresh=True))
