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


class PolishRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    action: PolishAction
    context: str | None = Field(None, max_length=12000)


class PolishChunkResponse(BaseModel):
    chunk: str
