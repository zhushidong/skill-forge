"""Tests for absorbed features: promote, field-log, apply-review, backup, version chain."""
from __future__ import annotations
import pytest
import json
import yaml
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
from skill_forge.versioning import (
    _diff_frontmatter,
    _diff_sections,
    compute_diff,
)
from skill_forge.adapters import to_text
from skill_forge.parsers import parse_external_file
from skill_forge import template_content
from skill_forge.templates import render_template


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
        # drills < 3 or avg_score < 60 -> no promotion
        assert check_auto_promote("draft", {"drills": 3, "avg_score": 50}) is None
        assert check_auto_promote("draft", {"drills": 2, "avg_score": 70}) is None
        # drills >= 3 and avg_score >= 60 -> promote
        assert check_auto_promote("draft", {"drills": 3, "avg_score": 60}) == "trained"

    def test_auto_promote_trained_to_tested(self):
        assert check_auto_promote("trained", {"field_tests": 0}) is None
        assert check_auto_promote("trained", {"field_tests": 1}) == "tested"

    def test_auto_promote_tested_to_mature(self):
        assert check_auto_promote("tested", {"field_tests": 4, "wins": 4, "avg_score": 80}) is None
        assert check_auto_promote("tested", {"field_tests": 5, "wins": 3, "avg_score": 70}) == "mature"
        # win_rate < 0.6 -> no promotion
        assert check_auto_promote("tested", {"field_tests": 5, "wins": 2, "avg_score": 80}) is None
        # avg_score < 70 -> no promotion
        assert check_auto_promote("tested", {"field_tests": 5, "wins": 5, "avg_score": 69}) is None

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


class TestDiffEngine:
    """Tests for field-level and section-level diff."""

    def test_diff_frontmatter_added_removed_changed(self):
        old = {"id": "a", "name": "Old", "status": "draft"}
        new = {"id": "a", "name": "New", "version": "1.0.0"}
        result = _diff_frontmatter(old, new)
        assert result["added"] == ["version"]
        assert result["removed"] == ["status"]
        assert len(result["changed"]) == 1
        assert result["changed"][0]["field"] == "name"

    def test_diff_frontmatter_nested_equal(self):
        old = {"metrics": {"drills": 3, "wins": 1}}
        new = {"metrics": {"wins": 1, "drills": 3}}
        result = _diff_frontmatter(old, new)
        assert result["changed"] == []

    def test_diff_sections_parses_headers(self):
        body = "# A\nline1\n# B\nline2\n"
        from skill_forge.versioning import _parse_sections
        sections = _parse_sections(body)
        assert "A" in sections
        assert "B" in sections
        assert sections["A"] == "line1"

    def test_diff_sections_detects_changed(self):
        old = "# Intro\nhello\n"
        new = "# Intro\nworld\n"
        result = _diff_sections(old, new)
        assert len(result["changed"]) == 1
        assert result["changed"][0]["title"] == "Intro"

    def test_diff_sections_detects_added_removed(self):
        old = "# A\ncontent\n"
        new = "# B\ncontent\n"
        result = _diff_sections(old, new)
        assert result["added"] == ["B"]
        assert result["removed"] == ["A"]

    def test_compute_diff_unified(self):
        diff = compute_diff("old", "new")
        assert "--- old version" in diff
        assert "+++ new version" in diff


class TestAdapterRouting:
    """Tests for adapter routing and value previews."""

    def test_json_adapter_routing(self):
        parsed = {
            "type": "json",
            "content": json.dumps({"name": "Agent", "goal": "test"}),
            "title": "agent.json",
        }
        text = to_text(parsed, asset_type="auto")
        assert "Agent" in text
        assert "test" in text

    def test_yaml_adapter_routing(self):
        parsed = {
            "type": "yaml",
            "content": yaml.safe_dump({"name": "Agent", "goal": "test"}),
            "title": "agent.yaml",
        }
        text = to_text(parsed, asset_type="auto")
        assert "Agent" in text

    def test_generic_agent_adapter_routing(self):
        parsed = {
            "type": "text",
            "content": '{"agent_name": "SalesBot", "instructions": "Sell things"}',
            "title": "external agent",
        }
        text = to_text(parsed, asset_type="agent")
        assert "SalesBot" in text
        assert "instructions" in text

    def test_parse_file_returns_file_type(self, tmp_path):
        p = tmp_path / "test.json"
        p.write_text('{"a": 1}', encoding="utf-8")
        parsed = parse_external_file(p)
        assert parsed["type"] == "json"
        # Simple JSON without agent/prompt hints defaults to "markdown"
        assert parsed["asset_type"] == "markdown"

    def test_parse_file_agent_definition(self, tmp_path):
        p = tmp_path / "agent.md"
        p.write_text("---\nasset_type: agent\n---\n# Agent\nSell", encoding="utf-8")
        parsed = parse_external_file(p)
        assert parsed["type"] == "markdown"
        assert parsed["asset_type"] == "markdown"


class TestProposeUpdateTemplate:
    """Tests for propose-update template usage."""

    def test_propose_update_template_exists(self):
        assert "propose_update.md" in template_content.TEMPLATES

    def test_propose_update_template_has_variables(self):
        content = template_content.TEMPLATES["propose_update.md"]
        for var in ("skill_name", "wins", "losses", "reviews_summary", "field_logs_summary"):
            assert "{{" + var + "}}" in content, f"Missing placeholder: {var}"

    def test_apply_review_template_exists(self):
        assert "apply_review.md" in template_content.TEMPLATES

    def test_distill_template_v5_has_new_schema(self):
        distill = template_content.TEMPLATES["distill.md"]
        assert "applicable_scenarios" in distill
        assert "customer_signals" in distill
        assert "forbidden_behaviors" in distill
