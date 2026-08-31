from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


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
    visual_context: str = ""
    image_dependency: str = ""


# --- Staged mistake workflow schemas ---


class QuestionDraftRequest(BaseModel):
    images: list[ImageInput] = Field(default_factory=list)
    text: str = ""


class QuestionDraftResponse(BaseModel):
    title: str
    question: str
    options: list[str] = Field(default_factory=list)
    visual_context: str = ""
    key_conditions: list[str] = Field(default_factory=list)
    candidate_answer: str = ""
    knowledge_points: str = ""
    question_type: str = ""
    subject: str = ""
    difficulty: str = "medium"
    tags: list[str] = Field(default_factory=list)
    image_dependency: str = "none"


class QuestionDraftConfirmRequest(BaseModel):
    draft: QuestionDraftResponse


class QuestionDraftConfirmResponse(BaseModel):
    status: Literal["confirmed"] = "confirmed"
    draft: QuestionDraftResponse
    confirmed_at: str = ""


class ErrorInterpretationRequest(BaseModel):
    question_draft: QuestionDraftResponse
    user_error_reason: str = Field(min_length=1)
    rejection_history: list[str] = Field(default_factory=list)


class ErrorInterpretationResponse(BaseModel):
    interpretation_id: str
    version: int = 1
    summary: str
    diagnosis: str
    root_cause: str
    knowledge_gap: str = ""
    suggested_correction: str = ""
    reasoning_trace: str = ""


class InterpretationRejectionRequest(BaseModel):
    question_draft: QuestionDraftResponse
    user_error_reason: str = Field(min_length=1)
    current_interpretation: ErrorInterpretationResponse
    rejection_reason: str = Field(min_length=1)
    rejection_history: list[str] = Field(default_factory=list)


class FinalAnalysisRequest(BaseModel):
    question_draft: QuestionDraftResponse
    user_error_reason: str
    accepted_interpretation: ErrorInterpretationResponse


class FinalAnalysisResponse(BaseModel):
    analysis: str
    error_reason: str
    key_step: str
    similar_traps: list[str] = Field(default_factory=list)
    generalization: str = ""
    review_advice: str = ""
    variant_questions: list[str] = Field(default_factory=list)
    accepted_interpretation_id: str = ""
    accepted_interpretation_version: int = 1


class DiagramStrategyRequest(BaseModel):
    question_draft: QuestionDraftResponse
    accepted_interpretation: ErrorInterpretationResponse
    final_analysis: FinalAnalysisResponse


class StructuredDiagramNode(BaseModel):
    id: str
    label: str
    x: float = 0
    y: float = 0
    highlighted: bool = False
    annotation: str = ""


class StructuredDiagramEdge(BaseModel):
    source: str
    target: str
    label: str = ""
    highlighted: bool = False
    weight: str = ""


class StructuredDiagramTableRow(BaseModel):
    cells: list[str]


class StructuredDiagramTable(BaseModel):
    headers: list[str]
    rows: list[StructuredDiagramTableRow]
    caption: str = ""


class StructuredDiagramData(BaseModel):
    diagram_type: Literal["graph", "table", "flowchart", "packet_slices"]
    title: str = ""
    nodes: list[StructuredDiagramNode] = Field(default_factory=list)
    edges: list[StructuredDiagramEdge] = Field(default_factory=list)
    table: StructuredDiagramTable | None = None
    mermaid: str = ""
    caption: str = ""
    error_reason_annotation: str = ""


class DiagramResponse(BaseModel):
    strategy: Literal["structured", "qwen_image_fallback"]
    strategy_reason: str = ""
    structured_data: StructuredDiagramData | None = None
    image_url: str = ""
    image_prompt: str = ""
    accepted_interpretation_id: str = ""
    accepted_interpretation_version: int = 1
    uses_error_interpretation: bool = True
