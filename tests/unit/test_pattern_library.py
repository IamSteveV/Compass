"""Tests for pattern library"""

import pytest
from src.patterns.library import PatternLibrary


def test_pattern_library_initialization(patterns_dir):
    """Test pattern library can be initialized"""
    library = PatternLibrary(repository_path=str(patterns_dir))
    assert library is not None
    assert len(library) > 0


def test_load_patterns(patterns_dir):
    """Test loading patterns from directory"""
    library = PatternLibrary(repository_path=str(patterns_dir))
    patterns = library.get_all_patterns()

    assert len(patterns) > 0
    assert patterns[0].metadata.id == "TEST-001"
    assert patterns[0].metadata.name == "Test Pattern"


def test_get_pattern_by_id(patterns_dir):
    """Test retrieving pattern by ID"""
    library = PatternLibrary(repository_path=str(patterns_dir))
    pattern = library.get_pattern("TEST-001")

    assert pattern is not None
    assert pattern.metadata.id == "TEST-001"


def test_get_nonexistent_pattern(patterns_dir):
    """Test retrieving nonexistent pattern"""
    library = PatternLibrary(repository_path=str(patterns_dir))
    pattern = library.get_pattern("NONEXISTENT")

    assert pattern is None


def test_get_approved_patterns(patterns_dir):
    """Test filtering approved patterns"""
    library = PatternLibrary(repository_path=str(patterns_dir))
    approved = library.get_approved_patterns()

    assert len(approved) > 0
    for pattern in approved:
        assert pattern.metadata.status == "approved"


def test_search_patterns(patterns_dir):
    """Test searching patterns"""
    library = PatternLibrary(repository_path=str(patterns_dir))
    results = library.search_patterns("test")

    assert len(results) > 0
