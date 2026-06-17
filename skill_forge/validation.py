"""Pydantic schemas for front matter validation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MaterialFrontMatter(BaseModel):
    """Schema for material front matter."""
    id: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern=r'^(article|book|chatlog|case|comment|prompt|workflow|external_agent|external_skill)$')
    source: str = Field(..., min_length=1, max_length=200)
    created_at: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric, hyphens, and underscores')
        return v


class SkillFrontMatter(BaseModel):
    """Schema for skill front matter."""
    id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    version: int = Field(default=1, ge=1)
    status: str = Field(..., pattern=r'^(draft|trained|tested|mature|retired)$')
    scenes: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)
    customer_types: list[str] = Field(default_factory=list)
    drills: int = Field(default=0, ge=0)
    field_tests: int = Field(default=0, ge=0)
    wins: int = Field(default=0, ge=0)
    losses: int = Field(default=0, ge=0)
    created_at: Optional[str] = None
    trained_at: Optional[str] = None
    tested_at: Optional[str] = None
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric, hyphens, and underscores')
        return v


class DrillFrontMatter(BaseModel):
    """Schema for drill front matter."""
    id: str = Field(..., min_length=1, max_length=100)
    skill_id: str = Field(..., min_length=1, max_length=100)
    created_at: Optional[str] = None
    scenario: str = Field(..., min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    
    @field_validator('id', 'skill_id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric, hyphens, and underscores')
        return v


class ReviewFrontMatter(BaseModel):
    """Schema for review front matter."""
    id: str = Field(..., min_length=1, max_length=100)
    skill_id: str = Field(..., min_length=1, max_length=100)
    created_at: Optional[str] = None
    win: bool = Field(...)
    reason: str = Field(default="")
    
    @field_validator('id', 'skill_id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric, hyphens, and underscores')
        return v


# ── Validation Functions ────────────────────────────────────────

SCHEMA_MAP = {
    'materials': MaterialFrontMatter,
    'skills': SkillFrontMatter,
    'drills': DrillFrontMatter,
    'reviews': ReviewFrontMatter,
}


def validate_front_matter(data: dict, category: str) -> tuple[bool, list[str]]:
    """Validate front matter against schema for the given category.
    
    Returns (is_valid, errors).
    """
    schema = SCHEMA_MAP.get(category)
    if not schema:
        return True, []  # No schema for this category, skip validation
    
    try:
        schema(**data)
        return True, []
    except Exception as e:
        errors = [str(err) for err in e.errors()]
        return False, errors
