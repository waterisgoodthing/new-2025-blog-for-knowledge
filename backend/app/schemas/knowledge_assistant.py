from pydantic import BaseModel, Field


class Suggestion(BaseModel):
    type: str
    title: str
    description: str
    targets: list[str] = Field(default_factory=list)
    action: str
    reason: str


class SuggestionListResponse(BaseModel):
    suggestions: list[Suggestion]


class ExecuteSuggestionRequest(BaseModel):
    type: str
    action: str
    targets: list[str] = Field(default_factory=list)
    tag: str | None = None
    folder_id: str | None = None
