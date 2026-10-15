from datetime import datetime
from typing import Literal

from pydantic import BaseModel


DiagnosticStatus = Literal["ok", "warning", "error", "unknown"]


class DiagnosticCheck(BaseModel):
    status: DiagnosticStatus


class DiagnosticChecks(BaseModel):
    service: DiagnosticCheck
    database: DiagnosticCheck
    storage: DiagnosticCheck
    auth: DiagnosticCheck


class DiagnosticsResponse(BaseModel):
    generated_at: datetime
    overall: Literal["ok", "degraded"]
    checks: DiagnosticChecks
