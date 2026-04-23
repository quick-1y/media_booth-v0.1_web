from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class AppSection(BaseModel):
    locale: str = "ru-RU"
    timezone: str = "Europe/Moscow"
    show_clock: bool = True
    clock_format: str = "HH:mm"


class ParserSection(BaseModel):
    server: str = ""
    path: str = ""
    token: str = ""


class ParkingSection(BaseModel):
    parser: ParserSection = Field(default_factory=ParserSection)


class ContentSection(BaseModel):
    working_hours: list[str] = Field(default_factory=lambda: ["Ежедневно: 08:00–22:00"])
    tariffs: list[str] = Field(default_factory=lambda: ["Первые 2 часа бесплатно", "С 3-го часа — 50 рублей/час"])

    @field_validator("working_hours", "tariffs")
    @classmethod
    def norm(cls, values: list[str]) -> list[str]:
        return [str(v).strip() for v in values if str(v).strip()]


class MediaSection(BaseModel):
    ads_path: str = "/data/ads"
    carousel_seconds: int = Field(default=8, ge=2, le=120)
    allowed_extensions: list[str] = Field(
        default_factory=lambda: [".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".webm", ".ogg"]
    )

    @field_validator("allowed_extensions")
    @classmethod
    def norm_list(cls, values: list[str]) -> list[str]:
        return [str(v).strip() for v in values if str(v).strip()]


class SettingsAccessSection(BaseModel):
    hidden_hotspot_enabled: bool = True


class DiagnosticsSection(BaseModel):
    show_raw_yaml_preview: bool = True
    show_parser_test: bool = True


class BlocksSection(BaseModel):
    show_working_hours: bool = True
    show_free_spaces: bool = True
    show_tariffs: bool = True
    show_carousel: bool = True


class UiSection(BaseModel):
    settings_access: SettingsAccessSection = Field(default_factory=SettingsAccessSection)
    diagnostics: DiagnosticsSection = Field(default_factory=DiagnosticsSection)
    blocks: BlocksSection = Field(default_factory=BlocksSection)


class AppearanceSection(BaseModel):
    accent_color: str = "#49a4ff"
    success_color: str = "#4be28a"
    warning_color: str = "#ffd05c"
    danger_color: str = "#ff8c7a"
    background_start: str = "#0b1620"
    background_end: str = "#071018"


class OperatingModeSection(BaseModel):
    manual_mode: Literal["normal", "closed"] = "normal"
    schedule_enabled: bool = False
    schedule_from: str = "08:00"
    schedule_to: str = "22:00"
    closed_text: str = "Parking is closed"


class AppConfig(BaseModel):
    version: Literal[1] = 1
    app: AppSection = Field(default_factory=AppSection)
    parking: ParkingSection = Field(default_factory=ParkingSection)
    content: ContentSection = Field(default_factory=ContentSection)
    media: MediaSection = Field(default_factory=MediaSection)
    ui: UiSection = Field(default_factory=UiSection)
    appearance: AppearanceSection = Field(default_factory=AppearanceSection)
    operating_mode: OperatingModeSection = Field(default_factory=OperatingModeSection)


class ParserTestRequest(BaseModel):
    server: str = ""
    path: str = ""
    token: str = ""
