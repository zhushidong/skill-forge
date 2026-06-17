"""Tests for skill_forge.validation module."""
from __future__ import annotations

import pytest

from skill_forge.validation import (
    MaterialFrontMatter,
    SkillFrontMatter,
    DrillFrontMatter,
    ReviewFrontMatter,
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
    """Tests for skill front matter schema."""

    def test_valid_skill(self):
        """Should accept valid skill front matter."""
        fm = SkillFrontMatter(
            id="skill-20260617",
            name="Test Skill",
            status="draft",
            scenes=["scene1"],
            signals=["signal1"],
            customer_types=["type1"],
        )
        assert fm.id == "skill-20260617"
        assert fm.status == "draft"
        assert fm.drills == 0
        assert fm.version == 1

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
                drills=-1,
            )


class TestDrillFrontMatter:
    """Tests for drill front matter schema."""

    def test_valid_drill(self):
        """Should accept valid drill front matter."""
        fm = DrillFrontMatter(
            id="drill-20260617",
            skill_id="skill-1",
            scenario="Test scenario",
            rating=5,
        )
        assert fm.rating == 5

    def test_rejects_invalid_rating(self):
        """Should reject rating outside 1-5 range."""
        with pytest.raises(Exception):
            DrillFrontMatter(
                id="drill-1",
                skill_id="skill-1",
                scenario="Test",
                rating=6,
            )


class TestReviewFrontMatter:
    """Tests for review front matter schema."""

    def test_valid_review(self):
        """Should accept valid review front matter."""
        fm = ReviewFrontMatter(
            id="review-20260617",
            skill_id="skill-1",
            win=True,
            reason="Customer was satisfied",
        )
        assert fm.win is True

    def test_requires_win_field(self):
        """Should require win field."""
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

    def test_unknown_category_passes(self):
        """Should pass validation for unknown categories."""
        data = {"any": "data"}
        is_valid, errors = validate_front_matter(data, "unknown_category")
        assert is_valid is True
        assert errors == []
