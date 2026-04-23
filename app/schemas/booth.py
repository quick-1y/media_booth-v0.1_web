from pydantic import BaseModel, field_validator


class BoothNamePayload(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def _not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Название стенда не может быть пустым")
        return v


BoothCreate = BoothNamePayload
BoothRename = BoothNamePayload
