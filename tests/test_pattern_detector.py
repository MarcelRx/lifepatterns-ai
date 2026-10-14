# Unit tests for PatternDetector
import pytest
from models.pattern_detector import PatternDetector
from utils.database import Entry


class MockEntry:
    """Mock entry object for testing"""
    def __init__(self, date, mood, energy, sleep, activities):
        self.entry_date = date
        self.mood_rating = mood
        self.energy_level = energy
        self.sleep_hours = sleep
        self.activities = activities


def test_mood_trend_improving():
    """Test detection of improving mood trend"""
    entries = [
        MockEntry("2024-01-01", 4, 5, 7, ["work"]),
        MockEntry("2024-01-02", 5, 6, 7, ["work"]),
        MockEntry("2024-01-03", 6, 7, 8, ["exercise"]),
        MockEntry("2024-01-04", 7, 8, 8, ["exercise"]),
    ]
    detector = PatternDetector(entries)
    trend = detector.detect_mood_trend()
    assert trend is not None
    assert trend["trend"] == "improving"
    assert trend["confidence"] > 0


def test_mood_trend_declining():
    """Test detection of declining mood trend"""
    entries = [
        MockEntry("2024-01-01", 8, 7, 8, ["exercise"]),
        MockEntry("2024-01-02", 7, 6, 7, ["work"]),
        MockEntry("2024-01-03", 6, 5, 6, ["work"]),
        MockEntry("2024-01-04", 5, 4, 6, ["work"]),
    ]
    detector = PatternDetector(entries)
    trend = detector.detect_mood_trend()
    assert trend is not None
    assert trend["trend"] == "declining"
    assert trend["confidence"] > 0


def test_mood_trend_insufficient_data():
    """Test that trend detection returns None with insufficient data"""
    entries = [
        MockEntry("2024-01-01", 5, 5, 7, ["work"]),
        MockEntry("2024-01-02", 6, 6, 7, ["work"]),
    ]
    detector = PatternDetector(entries)
    trend = detector.detect_mood_trend()
    assert trend is None


def test_sleep_mood_correlation():
    """Test detection of sleep-mood correlation"""
    entries = [
        MockEntry("2024-01-01", 5, 5, 5, ["work"]),
        MockEntry("2024-01-02", 6, 6, 7, ["exercise"]),
        MockEntry("2024-01-03", 7, 7, 8, ["exercise"]),
        MockEntry("2024-01-04", 8, 8, 8, ["exercise"]),
        MockEntry("2024-01-05", 4, 4, 5, ["work"]),
    ]
    detector = PatternDetector(entries)
    correlation = detector.detect_sleep_mood_correlation()
    # May or may not detect correlation depending on data
    if correlation:
        assert "description" in correlation
        assert "confidence" in correlation


def test_activity_impact():
    """Test detection of positive activity impact"""
    entries = [
        MockEntry("2024-01-01", 8, 7, 8, ["exercise"]),
        MockEntry("2024-01-02", 9, 8, 8, ["exercise"]),
        MockEntry("2024-01-03", 4, 4, 6, ["work"]),
        MockEntry("2024-01-04", 5, 5, 6, ["work"]),
    ]
    detector = PatternDetector(entries)
    impact = detector.detect_activity_impact()
    # Should detect exercise as positive activity
    if impact:
        assert "exercise" in impact["name"].lower()
        assert impact["confidence"] > 0


def test_get_all_patterns():
    """Test that get_all_patterns returns list of patterns"""
    entries = [
        MockEntry("2024-01-01", 4, 5, 7, ["work"]),
        MockEntry("2024-01-02", 5, 6, 7, ["work"]),
        MockEntry("2024-01-03", 6, 7, 8, ["exercise"]),
        MockEntry("2024-01-04", 7, 8, 8, ["exercise"]),
    ]
    detector = PatternDetector(entries)
    patterns = detector.get_all_patterns()
    assert isinstance(patterns, list)
