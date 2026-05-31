from pydantic import BaseModel


class ImageInput(BaseModel):
    base64: str
    mime_type: str


class AnalyzeRequest(BaseModel):
    images: list[ImageInput]


class TextAnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    title: str
    question: str
    correct_answer: str
    analysis: str
    knowledge_points: str
    subject: str
    difficulty: str
    tags: list[str]
