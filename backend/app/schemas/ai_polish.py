from enum import Enum

from pydantic import BaseModel, Field


class PolishAction(str, Enum):
    polish = "polish"
    summarize = "summarize"
    expand = "expand"
    continue_ = "continue"
    translate_en = "translate_en"
    translate_zh = "translate_zh"
    extract_tags = "extract_tags"
    generate_questions = "generate_questions"
    title = "title"
    outline = "outline"
    tags = "tags"
    diagram = "diagram"
    compare = "compare"
    mindmap = "mindmap"
    data_chart = "data_chart"
    custom = "custom"


class PolishRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    action: PolishAction
    context: str | None = Field(None, max_length=12000)
    title: str | None = Field(None, max_length=500)
    note_type: str | None = Field(None, max_length=20)
    existing_tags: list[str] | None = None
    custom_prompt: str | None = Field(None, max_length=2000)


class PolishChunkResponse(BaseModel):
    chunk: str
