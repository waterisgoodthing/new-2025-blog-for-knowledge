import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    registration_key: str | None = None


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    is_admin: bool

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: uuid.UUID
    auth_level: str
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionUserOut(BaseModel):
    id: uuid.UUID
    username: str
    is_admin: bool
    auth_level: str

    model_config = {"from_attributes": True}


class SetPasswordRequest(BaseModel):
    password: str = Field(..., min_length=6)


class OperatorRegOptionsRequest(BaseModel):
    device_name: str = Field(default="Operator Device", max_length=200)


class OperatorRegisterRequest(BaseModel):
    attestation: dict
    session_id: str = Field(..., min_length=16, max_length=64)
    device_name: str = Field(default="Operator Device", max_length=200)


class OperatorRegisterResponse(BaseModel):
    success: bool
    device_name: str | None = None
    message: str
