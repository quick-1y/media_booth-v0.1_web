from pydantic import BaseModel, field_validator


class BoothCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Название стенда не может быть пустым")
        return v


class BoothRename(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Название стенда не может быть пустым")
        return v


class BoothInfo(BaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str
