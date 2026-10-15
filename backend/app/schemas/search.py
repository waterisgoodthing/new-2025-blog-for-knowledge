from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=50, ge=1, le=100)


class SearchResult(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    type: str
    status: str
    hidden: bool
    updated_at: datetime

    model_config = {"from_attributes": True}
