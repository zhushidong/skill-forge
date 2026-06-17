"""Pydantic schemas for front matter validation.

Unified data model: validation.py, golden examples, and all commands
must use the SAME schema. This is the single source of truth.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Material Schema ────────────────────────────────────────────

class MaterialFrontMatter(BaseModel):
    """Schema for material front matter."""
    id: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern=r'^(article|book|chatlog|case|comment|prompt|workflow|external_agent|external_skill)$')
    source: str = Field(..., min_length=1, max_length=200)
    title: str = Field(default="")
    created_at: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric, hyphens, and underscores')
        return v


# ── Skill Schema ───────────────────────────────────────────────

class SkillMetrics(BaseModel):
    """Nested metrics block for Skill."""
    drills: int = Field(default=0, ge=0)
    field_tests: int = Field(default=0, ge=0)
    wins: int = Field(default=0, ge=0)
    losses: int = Field(default=0, ge=0)
    avg_score: float = Field(default=0.0, ge=0, le=100)
    last_used_at: str = Field(default="")


class SkillStrategy(BaseModel):
    """Strategy block for Skill."""
    name: str = Field(default="")
    steps: list[dict] = Field(default_factory=list)


class SkillEvidence(BaseModel):
    """Evidence chain for Skill."""
    source_materials: list[str] = Field(default_factory=list)
    drill_records: list[str] = Field(default_factory=list)
    review_records: list[str] = Field(default_factory=list)


class SkillFrontMatter(BaseModel):
    """Schema for skill front matter.
    
    This is the SINGLE source of truth. All code must read/write these fields.
    """
    id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    version: str = Field(default="1.0.0")
    status: str = Field(..., pattern=r'^(draft|trained|tested|mature|retired)$')
    domain: str = Field(default="other")
    problem: str = Field(default="")
    
    # Scenarios
    applicable_scenarios: list[str] = Field(default_factory=list)
    not_applicable_scenarios: list[str] = Field(default_factory=list)
    
    # Signals
    customer_signals: list[str] = Field(default_factory=list)
    
    # Strategy
    strategy: SkillStrategy = Field(default_factory=SkillStrategy)
    
    # Forbidden behaviors
    forbidden_behaviors: list[str] = Field(default_factory=list)
    
    # Version info
    parent_version: str = Field(default="")
    change_type: str = Field(default="initial")
    change_reason: str = Field(default="")
    changed_by: str = Field(default="")
    
    # Evidence chain
    evidence: SkillEvidence = Field(default_factory=SkillEvidence)
    
    # Metrics (nested)
    metrics: SkillMetrics = Field(default_factory=SkillMetrics)
    
    # Timestamps
    created_at: str = Field(default="")
    updated_at: str = Field(default="")
    trained_at: str = Field(default="")
    tested_at: str = Field(default="")
    mature_at: str = Field(default="")
    retired_at: str = Field(default="")
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric, hyphens, and underscores')
        return v


# ── Drill Schema ───────────────────────────────────────────────

class DrillScores(BaseModel):
    """Structured drill scores."""
    diagnosis: int = Field(default=0, ge=0, le=100)
    response_quality: int = Field(default=0, ge=0, le=100)
    next_step_control: int = Field(default=0, ge=0, le=100)
    risk_control: int = Field(default=0, ge=0, le=100)
    
    @property
    def average(self) -> float:
        scores = [self.diagnosis, self.response_quality, self.next_step_control, self.risk_control]
        return sum(scores) / len(scores) if scores else 0


class DrillFrontMatter(BaseModel):
    """Schema for drill front matter."""
    id: str = Field(..., min_length=1, max_length=100)
    skill_id: str = Field(..., min_length=1, max_length=100)
    created_at: str = Field(default="")
    persona: str = Field(default="普通客户")
    rounds: int = Field(default=5, ge=1)
    scores: DrillScores = Field(default_factory=DrillScores)
    average_score: float = Field(default=0.0, ge=0, le=100)
    result: str = Field(default="")  # success / partial_success / failure
    
    @field_validator('id', 'skill_id')
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('ID must contain only alphanumeric, hyphens, and underscores')
        return v


# ── Review Schema ──────────────────────────────────────────────

class ReviewScores(BaseModel):
    """Structured review scores."""
    adherence: int = Field(default=0, ge=0, le=100)
    outcome: int = Field(default=0, ge=0, le=100)
    improvement: int = Field(default=0, ge=0, le=100)
    skill_defect: int = Field(default=0, ge=0, le=100)
    
    @property
    def average(self) -> float:
        scores = [self.adherence, self.outcome, self.improvement, self.skill_defect]
        return sum(scores) / len(scores) if scores else 0


class ReviewFrontMatter(BaseModel):
    """Schema for review front matter."""
    id: str = Field(..., min_length=1, max_length=100)
    skill_id: str = Field(..., min_length=1, max_length=100)
    created_at: str = Field(default="")
    result: str = Field(..., pattern=r'^(推进|成交|失败|流失)$')
    source_path: str = Field(default="")
    scores: ReviewScores = Field(default_factory=ReviewScores)
    total_score: float = Field(default=0.0, ge=0, le=100)
    skill_defects: list[dict] = Field(default_factory=list)
    update_suggestions: list[dict] = Field(default_factory=list)
    
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
