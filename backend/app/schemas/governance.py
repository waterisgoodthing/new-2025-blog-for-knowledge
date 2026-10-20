from datetime import datetime

from pydantic import BaseModel


class GovernanceSection(BaseModel):
    status: str
    source: str
    count: int | None = None
    detail: str | None = None


class GovernanceSummary(BaseModel):
    generated_at: datetime
    ai: GovernanceSection
    tasks: GovernanceSection
    statistics: GovernanceSection
    report: GovernanceSection
    settings: GovernanceSection
