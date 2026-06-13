from pydantic import BaseModel, Field
from typing import Literal


class ImageInput(BaseModel):
    base64: str
    mime_type: str


class AnalyzeRequest(BaseModel):
    images: list[ImageInput]
    question: str | None = None
    my_answer: str | None = None
    correct_answer: str | None = None
    user_error_analysis: str | None = None
    analysis_mode: str | None = None


class TextAnalyzeRequest(BaseModel):
    text: str
    question: str | None = None
    my_answer: str | None = None
    correct_answer: str | None = None
    user_error_analysis: str | None = None
    analysis_mode: str | None = None


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
    personalized_diagnosis: str = ""
    misread_signal: str = ""
    next_time_checklist: list[str] = Field(default_factory=list)
    latex_warnings: list[str] = Field(default_factory=list)
