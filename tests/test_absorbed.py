"""Tests for absorbed features: promote, field-log, apply-review, backup, version chain."""
from __future__ import annotations
import pytest
from pathlib import Path
from skill_forge.commands._promote import (
    apply_result_to_metrics,
    bump_metric,
    check_auto_promote,
    validate_manual_promote,
    WIN_RESULTS,
    LOSS_RESULTS,
)
from skill_forge.storage import (
    read_markdown,
    write_markdown,
    timestamp_id,
    skill_path_by_status,
    all_skill_files,
    workspace_initialized,
)
from skill_forge.validation import validate_front_matter


class TestPromoteEngine:
    """Tests for _promote.py shared engine."""

    def test_bump_metric_basic(self):
        m = bump_metric({}, "drills", 1)
        assert m["drills"] == 1

    def test_bump_metric_existing(self):
        m = bump_metric({"drills": 3}, "drills", 1)
        assert m["drills"] == 4

    def test_bump_metric_none_value(self):
        m = bump_metric({"drills": None}, "drills", 1)
        assert m["drills"] == 1

    def test_apply_result_win(self):
        m, side = apply_result_to_metrics({"drills": 2}, "成交")
        assert side == "win"
        assert m["wins"] == 1
        assert m["field_tests"] == 1

    def test_apply_result_loss(self):
        m, side = apply_result_to_metrics({}, "搁置")
        assert side == "loss"
        assert m["losses"] == 1
        assert m["field_tests"] == 1

    def test_apply_result_neutral(self):
        m, side = apply_result_to_metrics({}, "其他")
        assert side == "neutral"
        assert m["field_tests"] == 1

    def test_auto_promote_draft_to_trained(self):
        # drills < 2 -> no promotion
        assert check_auto_promote("draft", {"drills": 1}) is None
        # drills >= 2 -> promote
        assert check_auto_promote("draft", {"drills": 2}) == "trained"

    def test_auto_promote_trained_to_tested(self):
        assert check_auto_promote("trained", {"wins": 1}) is None
        assert check_auto_promote("trained", {"wins": 2}) == "tested"

    def test_auto_promote_tested_to_mature(self):
        assert check_auto_promote("tested", {"wins": 4, "losses": 2}) is None
        assert check_auto_promote("tested", {"wins": 5, "losses": 1}) == "mature"

    def test_auto_promote_mature_no_rule(self):
        assert check_auto_promote("mature", {"wins": 100}) is None

    def test_validate_manual_promote_ok(self):
        ok, reason = validate_manual_promote("draft", "trained")
        assert ok is True

    def test_validate_manual_promote_skip_level(self):
        ok, reason = validate_manual_promote("draft", "mature")
        assert ok is False
        assert "skip" in reason.lower() or "cross" in reason.lower()

    def test_validate_manual_promote_demote(self):
        ok, reason = validate_manual_promote("mature", "draft")
        assert ok is False

    def test_validate_manual_promote_retired_from_any(self):
        ok, reason = validate_manual_promote("draft", "retired")
        assert ok is True

    def test_validate_manual_promote_from_retired(self):
        ok, reason = validate_manual_promote("retired", "draft")
        assert ok is False

    def test_validate_manual_promote_same_status(self):
        ok, reason = validate_manual_promote("draft", "draft")
        assert ok is False

    def test_validate_manual_promote_unknown_status(self):
        ok, reason = validate_manual_promote("draft", "unknown")
        assert ok is False


class TestStorageNew:
    """Tests for new storage functions."""

    def test_skill_path_by_status(self):
        p = skill_path_by_status("draft", "test-123")
        assert "draft" in str(p)
        assert "test-123.md" in str(p)

    def test_skill_path_by_status_all_statuses(self):
        for status in ["draft", "trained", "tested", "mature", "retired"]:
            p = skill_path_by_status(status, "test-123")
            assert status in str(p)

    def test_timestamp_id_uniqueness(self):
        ids = {timestamp_id("test") for _ in range(100)}
        # With millisecond+random, all should be unique
        assert len(ids) == 100


class TestSchemaExtended:
    """Tests for extended schema fields."""

    def test_skill_with_supersedes(self):
        data = {
            "id": "skill-123",
            "name": "Test Skill",
            "version": "2.0.0",
            "status": "draft",
            "supersedes": "skill-122",
            "superseded_by": "",
            "inherited_metrics": True,
        }
        is_valid, errors = validate_front_matter(data, "skills")
        assert is_valid

    def test_skill_with_inherited_metrics(self):
        data = {
            "id": "skill-123",
            "name": "Test Skill",
            "version": "2.0.0",
            "status": "trained",
            "metrics": {
                "drills": 5,
                "field_tests": 3,
                "wins": 2,
                "losses": 1,
                "avg_score": 75.0,
                "last_used_at": "",
            },
        }
        is_valid, errors = validate_front_matter(data, "skills")
        assert is_valid
