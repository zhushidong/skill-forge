"""Tests for skill_forge.validation module.

Updated to match unified schema: version is string, metrics is nested.
"""
from __future__ import annotations

import pytest

from skill_forge.validation import (
    MaterialFrontMatter,
    SkillFrontMatter,
    SkillMetrics,
    DrillFrontMatter,
    DrillScores,
    ReviewFrontMatter,
    ReviewScores,
    validate_front_matter,
)


class TestMaterialFrontMatter:
    """Tests for material front matter schema."""

    def test_valid_material(self):
        """Should accept valid material front matter."""
        fm = MaterialFrontMatter(
            id="material-20260617",
            type="article",
            source="test.md",
            tags=["tag1", "tag2"],
        )
        assert fm.id == "material-20260617"
        assert fm.type == "article"

    def test_rejects_invalid_type(self):
        """Should reject invalid material type."""
        with pytest.raises(Exception):
            MaterialFrontMatter(
                id="material-1",
                type="invalid_type",
                source="test.md",
            )

    def test_rejects_empty_id(self):
        """Should reject empty ID."""
        with pytest.raises(Exception):
            MaterialFrontMatter(
                id="",
                type="article",
                source="test.md",
            )

    def test_rejects_special_chars_in_id(self):
        """Should reject special characters in ID."""
        with pytest.raises(Exception):
            MaterialFrontMatter(
                id="material/../../../etc",
                type="article",
                source="test.md",
            )


class TestSkillFrontMatter:
    """Tests for skill front matter schema (unified)."""

    def test_valid_skill(self):
        """Should accept valid skill front matter with unified schema."""
        fm = SkillFrontMatter(
            id="skill-20260617",
            name="Test Skill",
            version="1.0.0",
            status="draft",
            domain="sales",
            problem="客户嫌贵",
            applicable_scenarios=["价格异议"],
            customer_signals=["太贵了"],
        )
        assert fm.id == "skill-20260617"
        assert fm.version == "1.0.0"
        assert fm.status == "draft"
        assert fm.metrics.drills == 0

    def test_version_is_string(self):
        """Version must be string, not int."""
        fm = SkillFrontMatter(
            id="skill-1",
            name="Test",
            version="0.1.0",
            status="draft",
        )
        assert fm.version == "0.1.0"
        assert isinstance(fm.version, str)

    def test_metrics_is_nested(self):
        """Metrics must be nested dict, not top-level fields."""
        fm = SkillFrontMatter(
            id="skill-1",
            name="Test",
            status="draft",
            metrics=SkillMetrics(drills=3, wins=2, avg_score=75.0),
        )
        assert fm.metrics.drills == 3
        assert fm.metrics.wins == 2
        assert fm.metrics.avg_score == 75.0

    def test_rejects_invalid_status(self):
        """Should reject invalid status."""
        with pytest.raises(Exception):
            SkillFrontMatter(
                id="skill-1",
                name="Test",
                status="invalid_status",
            )

    def test_negative_metrics_rejected(self):
        """Should reject negative metric values."""
        with pytest.raises(Exception):
            SkillFrontMatter(
                id="skill-1",
                name="Test",
                status="draft",
                metrics=SkillMetrics(drills=-1),
            )


class TestDrillFrontMatter:
    """Tests for drill front matter schema."""

    def test_valid_drill(self):
        """Should accept valid drill front matter with scores."""
        fm = DrillFrontMatter(
            id="drill-20260617",
            skill_id="skill-1",
            persona="预算不足型客户",
            rounds=5,
            scores=DrillScores(
                diagnosis=75,
                response_quality=70,
                next_step_control=65,
                risk_control=80,
            ),
            average_score=72.5,
            result="partial_success",
        )
        assert fm.scores.diagnosis == 75
        assert fm.average_score == 72.5
        assert fm.result == "partial_success"

    def test_scores_average(self):
        """Scores should calculate average correctly."""
        scores = DrillScores(diagnosis=80, response_quality=80, next_step_control=80, risk_control=80)
        assert scores.average == 80.0

    def test_rejects_invalid_score(self):
        """Should reject score outside 0-100 range."""
        with pytest.raises(Exception):
            DrillFrontMatter(
                id="drill-1",
                skill_id="skill-1",
                scores=DrillScores(diagnosis=101),
            )


class TestReviewFrontMatter:
    """Tests for review front matter schema."""

    def test_valid_review(self):
        """Should accept valid review front matter with scores."""
        fm = ReviewFrontMatter(
            id="review-20260617",
            skill_id="skill-1",
            result="推进",
            scores=ReviewScores(
                adherence=75,
                outcome=80,
                improvement=70,
                skill_defect=60,
            ),
            total_score=71.25,
        )
        assert fm.result == "推进"
        assert fm.scores.adherence == 75
        assert fm.total_score == 71.25

    def test_rejects_invalid_result(self):
        """Should reject invalid result."""
        with pytest.raises(Exception):
            ReviewFrontMatter(
                id="review-1",
                skill_id="skill-1",
                result="invalid",
            )

    def test_requires_result_field(self):
        """Should require result field."""
        with pytest.raises(Exception):
            ReviewFrontMatter(
                id="review-1",
                skill_id="skill-1",
            )


class TestValidateFrontMatter:
    """Tests for validate_front_matter function."""

    def test_validates_material(self):
        """Should validate material front matter correctly."""
        data = {
            "id": "material-1",
            "type": "article",
            "source": "test.md",
        }
        is_valid, errors = validate_front_matter(data, "materials")
        assert is_valid is True
        assert errors == []

    def test_catches_invalid_material(self):
        """Should catch invalid material front matter."""
        data = {
            "id": "material-1",
            "type": "invalid_type",
            "source": "test.md",
        }
        is_valid, errors = validate_front_matter(data, "materials")
        assert is_valid is False
        assert len(errors) > 0

    def test_validates_skill(self):
        """Should validate skill front matter with unified schema."""
        data = {
            "id": "skill-1",
            "name": "Test Skill",
            "version": "1.0.0",
            "status": "draft",
            "metrics": {"drills": 0, "field_tests": 0, "wins": 0, "losses": 0, "avg_score": 0},
        }
        is_valid, errors = validate_front_matter(data, "skills")
        assert is_valid is True

    def test_unknown_category_passes(self):
        """Should pass validation for unknown categories."""
        data = {"any": "data"}
        is_valid, errors = validate_front_matter(data, "unknown_category")
        assert is_valid is True
        assert errors == []
