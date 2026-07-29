import uuid
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator, model_validator

HomeSection = Literal["today", "activity", "stats", "storage"]
DEFAULT_SECTION_ORDER = ["today", "activity", "stats", "storage"]
LEARNING_ACTION_SECTIONS = {"today", "activity"}


class HomePreferences(BaseModel):
    show_welcome: bool = True
    section_order: list[HomeSection] = Field(default_factory=lambda: list(DEFAULT_SECTION_ORDER), max_length=4)
    hidden_sections: list[HomeSection] = Field(default_factory=list, max_length=3)

    @field_validator("section_order", "hidden_sections")
    @classmethod
    def reject_duplicate_sections(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("sections must not contain duplicates")
        return value

    @model_validator(mode="after")
    def keep_a_safe_section_visible(self) -> "HomePreferences":
        if set(self.section_order) != set(DEFAULT_SECTION_ORDER):
            raise ValueError("section_order must include each supported home section exactly once")
        if len(self.hidden_sections) >= len(DEFAULT_SECTION_ORDER):
            raise ValueError("at least one home section must remain visible")
        if not LEARNING_ACTION_SECTIONS.intersection(DEFAULT_SECTION_ORDER).difference(self.hidden_sections):
            raise ValueError("at least one learning action section must remain visible")
        return self


class AdminProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    identity_title: str = Field(default="", max_length=100)
    signature: str = Field(default="", max_length=300)
    welcome_message: str = Field(default="", max_length=300)
    timezone: str = Field(default="Asia/Shanghai", min_length=1, max_length=64)
    home_preferences: HomePreferences = Field(default_factory=HomePreferences)

    @field_validator("display_name", "identity_title", "signature", "welcome_message")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def require_display_name(self) -> "AdminProfileUpdate":
        if not self.display_name:
            raise ValueError("display_name must not be blank")
        return self

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        value = value.strip()
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise ValueError("timezone must be a valid IANA timezone") from error
        return value


class AdminProfileOut(AdminProfileUpdate):
    id: uuid.UUID
    user_id: uuid.UUID

    model_config = {"from_attributes": True}
