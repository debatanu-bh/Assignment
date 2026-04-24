from pydantic import BaseModel, Field, field_validator
from typing import Optional

class DeviceNameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Device name cannot be empty or whitespace only")
        return v.strip()


class DeviceNameResponse(BaseModel):
    name: str
    updated_at: Optional[str] = None


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None