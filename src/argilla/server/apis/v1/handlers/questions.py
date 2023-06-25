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

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from argilla.server.contexts import datasets
from argilla.server.database import get_db
from argilla.server.policies import QuestionPolicyV1, authorize
from argilla.server.schemas.v1.questions import Question
from argilla.server.security import auth
from argilla.server.security.model import User

router = APIRouter(tags=["questions"])


@router.delete("/questions/{question_id}", response_model=Question)
def delete_question(
    *,
    db: Session = Depends(get_db),
    question_id: UUID,
    current_user: User = Security(auth.get_current_user),
):
    question = datasets.get_question_by_id(db, question_id)

    authorize(current_user, QuestionPolicyV1.delete(question))
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id `{question_id}` not found",
        )

    # TODO: We should split API v1 into different FastAPI apps so we can customize error management.
    # After mapping ValueError to 422 errors for API v1 then we can remove this try except.
    try:
        datasets.delete_question(db, question)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

    return question
