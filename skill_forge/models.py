from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


def now_iso() -> str:
    """Return current ISO timestamp."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _now_iso() -> str:
    return now_iso()


@dataclass
class Material:
    id: str
    type: str
    title: str
    tags: list[str] = field(default_factory=list)
    note: str = ""
    source_path: str = ""
    created_at: str = field(default_factory=_now_iso)


@dataclass
class Skill:
    id: str
    name: str
    version: str = "0.1.0"
    status: str = "draft"
    source_ids: list[str] = field(default_factory=list)
    source_type: str = "material"
    scenes: list[str] = field(default_factory=list)
    customer_stages: list[str] = field(default_factory=list)
    customer_types: list[str] = field(default_factory=list)
    signals: list[str] = field(default_factory=list)
    avoid_when: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=lambda: {"drills": 0, "field_tests": 0, "wins": 0, "losses": 0})
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)


@dataclass
class Drill:
    id: str
    skill_id: str
    persona: str = ""
    rounds: int = 5
    created_at: str = field(default_factory=_now_iso)


@dataclass
class Review:
    id: str
    skill_id: str = ""
    result: str = ""
    created_at: str = field(default_factory=_now_iso)


@dataclass
class Recommendation:
    id: str
    source_file: str = ""
    created_at: str = field(default_factory=_now_iso)
