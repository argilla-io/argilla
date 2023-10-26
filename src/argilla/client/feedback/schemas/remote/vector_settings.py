from datetime import datetime
from uuid import UUID

from argilla.client.feedback.schemas.vector_settings import VectorSettings


class RemoteVectorSettings(VectorSettings):
    id: UUID
    inserted_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True