"""Tests for skill_forge.storage module."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from skill_forge.config import PROJECT_ROOT, DATA_DIR, TEMPLATES_DIR
from skill_forge.storage import (
    _validate_path,
    safe_read_file,
    write_markdown,
    read_markdown,
    slugify,
    timestamp_id,
    MAX_FILE_SIZE,
)


class TestValidatePath:
    """Tests for path validation security."""

    def test_rejects_path_traversal(self):
        """C1: Should reject paths that escape allowed directories."""
        with pytest.raises(ValueError, match="Path escapes allowed directories"):
            _validate_path(Path("../../etc/passwd"))

    def test_rejects_absolute_system_path(self):
        """Should reject absolute paths outside allowed dirs."""
        with pytest.raises(ValueError, match="Path escapes allowed directories"):
            _validate_path(Path("/etc/passwd"))

    def test_accepts_valid_data_dir_path(self):
        """Should accept paths within data directory."""
        valid_path = PROJECT_ROOT / "data" / "skills" / "draft" / "test.md"
        result = _validate_path(valid_path)
        assert result == valid_path.resolve()

    def test_accepts_valid_templates_dir_path(self):
        """Should accept paths within templates directory."""
        valid_path = PROJECT_ROOT / "templates" / "test.md"
        result = _validate_path(valid_path)
        assert result == valid_path.resolve()


class TestSafeReadFile:
    """Tests for safe file reading with size limits."""

    def test_rejects_large_files(self):
        """H1: Should reject files larger than MAX_FILE_SIZE."""
        large_path = DATA_DIR / "test_large.md"
        large_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Write a file larger than limit
            large_path.write_text("x" * (MAX_FILE_SIZE + 1), encoding="utf-8")
            
            with pytest.raises(ValueError, match="文件过大"):
                safe_read_file(large_path)
        finally:
            if large_path.exists():
                large_path.unlink()

    def test_accepts_normal_files(self):
        """Should accept files within size limit."""
        test_path = DATA_DIR / "test_normal.md"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            test_path.write_text("normal content", encoding="utf-8")
            content = safe_read_file(test_path)
            assert content == "normal content"
        finally:
            if test_path.exists():
                test_path.unlink()

    def test_rejects_path_traversal(self):
        """C2: Should reject path traversal in safe_read_file."""
        with pytest.raises(ValueError, match="Path escapes allowed directories"):
            safe_read_file(Path("../../etc/passwd"))


class TestWriteReadMarkdown:
    """Tests for markdown write/read operations."""

    def test_write_read_roundtrip(self):
        """Should write and read markdown files correctly."""
        test_path = DATA_DIR / "test_roundtrip.md"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            frontmatter = {"id": "test-1", "name": "Test", "version": 1}
            body = "This is test content."
            
            write_markdown(test_path, frontmatter, body)
            
            read_fm, read_body = read_markdown(test_path)
            assert read_fm["id"] == "test-1"
            assert read_fm["name"] == "Test"
            assert read_body == "This is test content."
        finally:
            if test_path.exists():
                test_path.unlink()

    def test_write_rejects_invalid_path(self):
        """Should reject writes to invalid paths."""
        with pytest.raises(ValueError, match="Path escapes allowed directories"):
            write_markdown(
                Path("../../etc/malicious.md"),
                {"id": "bad"},
                "evil content"
            )


class TestSlugify:
    """Tests for filename slug generation."""

    def test_basic_slug(self):
        """Should convert basic text to slug."""
        assert slugify("Hello World") == "Hello-World"

    def test_chinese_characters(self):
        """Should handle Chinese characters."""
        result = slugify("测试标题")
        assert result == "测试标题"

    def test_special_characters(self):
        """Should remove special characters."""
        result = slugify("hello@world.com!")
        assert "@" not in result
        assert "!" not in result

    def test_length_limit(self):
        """Should limit slug length to 80 chars."""
        long_text = "a" * 100
        result = slugify(long_text)
        assert len(result) <= 80

    def test_empty_text(self):
        """Should generate timestamp-based slug for empty text."""
        result = slugify("")
        assert result.startswith("file-")


class TestTimestampId:
    """Tests for timestamp ID generation."""

    def test_basic_format(self):
        """Should generate ID with prefix and timestamp."""
        result = timestamp_id("material")
        assert result.startswith("material-")
        assert len(result) > 10

    def test_different_prefixes(self):
        """Should generate different IDs for different prefixes."""
        id1 = timestamp_id("material")
        id2 = timestamp_id("skill")
        # They might be same timestamp but different prefixes
        assert id1.startswith("material-")
        assert id2.startswith("skill-")
