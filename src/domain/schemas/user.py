import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserAuthSchema(BaseModel):

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"],
    )

    password: SecretStr = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password",
        examples=["StrongPassword123!"],
    )


class UserResponseSchema(BaseModel):

    id: uuid.UUID = Field(
        ...,
        description="Unique user identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"],
    )

    created_at: datetime = Field(
        ...,
        description="Date and time when the user was created",
        examples=["2026-10-02T15:30:00Z"],
    )

    model_config = ConfigDict(
        from_attributes=True,
    )
