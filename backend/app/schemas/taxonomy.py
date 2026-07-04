from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class _NamedModel(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be blank")
        return normalized


class SubjectCreate(_NamedModel):
    name: str = Field(max_length=100)
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("name must not be null")
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be blank")
        return normalized


class SubjectOut(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterCreate(_NamedModel):
    subject_id: int
    name: str = Field(max_length=150)
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0


class ChapterUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    description: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("name must not be null")
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be blank")
        return normalized


class ChapterOut(BaseModel):
    id: int
    subject_id: int
    name: str
    description: str | None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgePointCreate(_NamedModel):
    subject_id: int
    chapter_id: int | None = None
    name: str = Field(max_length=200)
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0


class KnowledgePointUpdate(BaseModel):
    subject_id: int | None = None
    chapter_id: int | None = None
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("name must not be null")
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be blank")
        return normalized


class KnowledgePointOut(BaseModel):
    id: int
    subject_id: int
    chapter_id: int | None
    name: str
    description: str | None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
