from pydantic import BaseModel, Field, field_validator
from typing import Optional


class DeviceNameRequest(BaseModel):
    """Model for device name change request"""
    name: str = Field(..., min_length=1, max_length=100, description="Device name")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate device name contains only allowed characters"""
        if not v.strip():
            raise ValueError("Device name cannot be empty or whitespace only")
        return v.strip()


class DeviceNameResponse(BaseModel):
    """Model for device name response"""
    name: str
    updated_at: Optional[str] = None


class AuthRequest(BaseModel):
    """Model for authentication request"""
    username: str
    password: str


class AuthResponse(BaseModel):
    """Model for authentication response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None