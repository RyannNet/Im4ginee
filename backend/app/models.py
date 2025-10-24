from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    generations = relationship("Generation", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    type = Column(String(20), nullable=False)  # image|video|upscale
    mode = Column(String(20), nullable=False)  # sfw|nsfw|nsfw_smart

    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)

    seed = Column(Integer, nullable=True)
    steps = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    style = Column(String(50), nullable=True)

    source_path = Column(String(1024), nullable=True)  # for img2img or video source
    output_path = Column(String(1024), nullable=True)

    status = Column(String(20), default="queued", nullable=False)  # queued|running|completed|failed|blocked|flagged
    error = Column(Text, nullable=True)

    nsfw_tags = Column(String(255), nullable=True)  # comma-separated tags: explicit,soft,fetish
    nsfw_action = Column(String(20), nullable=True)  # allow|flag|block

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="generations")
    reviews = relationship("ModerationReview", back_populates="generation", cascade="all, delete-orphan")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    generation_id = Column(Integer, ForeignKey("generations.id"), index=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="favorites")


class ModerationReview(Base):
    __tablename__ = "moderation_reviews"

    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), index=True, nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    action = Column(String(20), nullable=False)  # allow|flag|block
    tags = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    generation = relationship("Generation", back_populates="reviews")
