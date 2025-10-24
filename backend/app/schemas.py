from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: int
    exp: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True


# Generation
class GenerationCreate(BaseModel):
    type: str  # image|video|upscale
    mode: str  # sfw|nsfw|nsfw_smart
    prompt: str
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    steps: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    style: Optional[str] = None
    source_path: Optional[str] = None


class GenerationOut(BaseModel):
    id: int
    type: str
    mode: str
    prompt: str
    negative_prompt: Optional[str]
    seed: Optional[int]
    steps: Optional[int]
    width: Optional[int]
    height: Optional[int]
    style: Optional[str]
    source_path: Optional[str]
    output_path: Optional[str]
    status: str
    error: Optional[str]
    nsfw_tags: Optional[str]
    nsfw_action: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FavoriteOut(BaseModel):
    id: int
    generation_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ModerationReviewCreate(BaseModel):
    action: str
    tags: Optional[str] = None
    notes: Optional[str] = None


class ModerationReviewOut(BaseModel):
    id: int
    generation_id: int
    reviewer_id: int
    action: str
    tags: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
