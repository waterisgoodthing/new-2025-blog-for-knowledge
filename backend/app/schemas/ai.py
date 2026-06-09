from pydantic import BaseModel, Field
from typing import Literal


class ImageInput(BaseModel):
    base64: str
    mime_type: str


class AnalyzeRequest(BaseModel):
    images: list[ImageInput]


class TextAnalyzeRequest(BaseModel):
    text: str


class DiagramItem(BaseModel):
    type: Literal["flowchart", "timeline", "formula_breakdown", "network_topology", "geometry", "state_machine"]
    title: str
    mermaid: str


class AnalyzeResponse(BaseModel):
    title: str
    question: str
    correct_answer: str
    analysis: str
    knowledge_points: str
    subject: str
    difficulty: str
    tags: list[str]
    error_reason: str = ""
    key_step: str = ""
    similar_traps: list[str] = Field(default_factory=list)
    generalization: str = ""
    review_advice: str = ""
    variant_questions: list[str] = Field(default_factory=list)
    related_notes: list[dict] = Field(default_factory=list)
    diagrams: list[DiagramItem] = Field(default_factory=list)
