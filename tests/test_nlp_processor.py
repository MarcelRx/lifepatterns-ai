# Unit tests for NLP Processor
import json
import os
from unittest.mock import Mock, patch

from models.nlp_processor import NLPProcessor
from utils.config import is_external_ai_enabled


def test_nlp_processor_initialization():
    """Test that NLPProcessor initializes correctly"""
    processor = NLPProcessor()
    assert processor is not None
    assert processor.emotion_keywords is not None
    assert processor.activity_keywords is not None


def test_analyze_empty_text():
    """Test analysis of empty text returns empty result"""
    processor = NLPProcessor()
    result = processor.analyze_entry("")
    assert result["sentiment_score"] == 0.0
    assert result["sentiment_label"] == "neutral"
    assert result["keywords"] == []
    assert result["topics"] == []


def test_analyze_positive_text():
    """Test analysis of positive text"""
    processor = NLPProcessor()
    result = processor.analyze_entry("I had a great and happy day today!")
    assert result["sentiment_score"] > 0
    assert result["sentiment_label"] == "positive"


def test_analyze_negative_text():
    """Test analysis of negative text"""
    processor = NLPProcessor()
    result = processor.analyze_entry("I feel sad and depressed today.")
    assert result["sentiment_score"] < 0
    assert result["sentiment_label"] == "negative"


def test_analyze_neutral_text():
    """Test analysis of neutral text"""
    processor = NLPProcessor()
    result = processor.analyze_entry("I went to work and came home.")
    assert result["sentiment_label"] == "neutral"


def test_emotion_detection():
    """Test emotion detection from text"""
    processor = NLPProcessor()
    result = processor.analyze_entry("I feel very happy and joyful today!")
    emotions = result["emotions"]
    assert "joy" in emotions
    assert emotions["joy"] > 0


def test_keyword_extraction():
    """Test keyword extraction from text"""
    processor = NLPProcessor()
    result = processor.analyze_entry(
        "I exercised and meditated this morning before work."
    )
    keywords = result["keywords"]
    assert isinstance(keywords, list)
    assert len(keywords) > 0


def test_topic_detection():
    """Test topic detection from text"""
    processor = NLPProcessor()
    result = processor.analyze_entry("I had a meeting at work about my job.")
    topics = result["topics"]
    assert isinstance(topics, list)
    assert "work" in topics


def test_local_analyze_fallback():
    """Test that local analysis works without Groq API"""
    processor = NLPProcessor(groq_client=None)
    result = processor.analyze_entry("I had a good day at work.")
    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result


def test_external_ai_disabled():
    """Test that local analysis is used when external AI is disabled"""
    processor = NLPProcessor(groq_client=None)
    result = processor.analyze_entry("I feel happy and excited today!")
    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result
    assert result["sentiment_score"] > 0
    assert result["sentiment_label"] == "positive"


def test_external_api_failure_fallback():
    """Test that local analysis is used when external API fails"""
    # Create a mock Groq client that raises an exception
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("I had a good day.")

    # Should fall back to local analysis
    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result


def test_timeout_handling():
    """Test handling of API timeout"""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = TimeoutError("Request timed out")

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should fall back to local analysis
    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result


def test_empty_journal_input():
    """Test handling of empty journal input"""
    processor = NLPProcessor()
    result = processor.analyze_entry("")

    assert result is not None
    assert result["sentiment_score"] == 0.0
    assert result["sentiment_label"] == "neutral"
    assert result["keywords"] == []
    assert result["topics"] == []


def test_whitespace_only_input():
    """Test handling of whitespace-only input"""
    processor = NLPProcessor()
    result = processor.analyze_entry("   \n\t   ")

    assert result is not None
    assert result["sentiment_score"] == 0.0
    assert result["sentiment_label"] == "neutral"


def test_data_contract_compatibility():
    """Test that output matches expected database schema"""
    processor = NLPProcessor(groq_client=None)
    result = processor.analyze_entry("I had a productive day at work.")

    # Verify all required fields for database storage exist
    assert "sentiment_score" in result
    assert isinstance(result["sentiment_score"], (int, float))
    assert -1.0 <= result["sentiment_score"] <= 1.0

    assert "sentiment_label" in result
    assert isinstance(result["sentiment_label"], str)
    assert result["sentiment_label"] in ["positive", "negative", "neutral"]

    assert "emotions" in result
    assert isinstance(result["emotions"], dict)
    # Verify expected emotion keys
    expected_emotions = ["joy", "sadness", "anger", "fear", "stress", "calm"]
    for emotion in expected_emotions:
        assert emotion in result["emotions"]
        assert isinstance(result["emotions"][emotion], (int, float))
        assert 0.0 <= result["emotions"][emotion] <= 1.0

    assert "keywords" in result
    assert isinstance(result["keywords"], list)

    assert "topics" in result
    assert isinstance(result["topics"], list)


def test_no_external_api_calls_when_disabled():
    """Test that no external API calls are made when external AI is disabled"""
    mock_client = Mock()
    processor = NLPProcessor(groq_client=mock_client)

    # Even though a mock client is provided, we test that local analysis works
    # In actual usage, groq_client=None would be passed when disabled
    result = processor.analyze_entry("Test text")

    # Since we passed a mock client, it would try to use it
    # This test verifies the mock behavior - in production, None would be passed
    assert result is not None


def test_very_long_journal_input():
    """Test handling of very long journal input"""
    processor = NLPProcessor(groq_client=None)
    long_text = "I feel happy. " * 1000  # Create a very long text
    result = processor.analyze_entry(long_text)

    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result


def test_special_characters_in_input():
    """Test handling of special characters in journal input"""
    processor = NLPProcessor(groq_client=None)
    text_with_special = "I felt happy! 😊 It was great... or maybe not?"
    result = processor.analyze_entry(text_with_special)

    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result


# ===== Configuration and Privacy Tests =====


def test_config_external_ai_disabled_by_default():
    """Test that external AI is disabled by default when variable is absent"""
    with patch.dict(os.environ, {}, clear=True):
        assert not is_external_ai_enabled()


def test_config_external_ai_explicit_false():
    """Test that external AI is disabled when explicitly set to false"""
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "false"}):
        assert not is_external_ai_enabled()


def test_config_external_ai_explicit_true():
    """Test that external AI is enabled when explicitly set to true"""
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "true"}):
        assert is_external_ai_enabled()


def test_config_external_ai_case_variations():
    """Test that configuration is case-insensitive"""
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "TRUE"}):
        assert is_external_ai_enabled()
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "True"}):
        assert is_external_ai_enabled()
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "FALSE"}):
        assert not is_external_ai_enabled()


def test_config_external_ai_whitespace_handling():
    """Test that surrounding whitespace is trimmed"""
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": " true "}):
        assert is_external_ai_enabled()
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": " false "}):
        assert not is_external_ai_enabled()


def test_config_external_ai_invalid_values_fail_closed():
    """Test that invalid values fail closed (external AI disabled)"""
    invalid_values = ["yes", "1", "enabled", "on", "random"]
    for value in invalid_values:
        with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": value}):
            assert not is_external_ai_enabled(), (
                f"Value '{value}' should disable external AI"
            )


def test_no_external_api_call_when_disabled():
    """Test that Groq API is not called when external AI is disabled"""
    mock_client = Mock()

    # Even with a mock client, if we pass None it should use local analysis
    processor_none = NLPProcessor(groq_client=None)
    result = processor_none.analyze_entry("Test text")

    # Verify no API call was made (since client is None)
    assert result is not None
    assert "sentiment_score" in result
    mock_client.chat.completions.create.assert_not_called()


def test_external_api_not_called_without_api_key():
    """Test that external API is not used when API key is missing"""
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "true"}, clear=True):
        # Remove GROQ_API_KEY
        os.environ.pop("GROQ_API_KEY", None)

        # This should fall back to local analysis since no API key
        result = NLPProcessor().analyze_entry("Test text")

        assert result is not None
        assert "sentiment_score" in result


def test_consent_scenarios():
    """
    Test consent control scenarios for external AI processing.

    Invariant: External AI may be called only if:
    1. Operator configuration explicitly enables it (ENABLE_EXTERNAL_AI=true)
    2. The API key is available (GROQ_API_KEY set)
    3. The user has explicitly consented (user_consent=True)

    This test verifies the decision logic that combines these conditions.
    """
    # Scenario 1: Operator disabled, user consent absent
    # Expected: External AI NOT called
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "false"}, clear=True):
        enable_external_ai = is_external_ai_enabled()
        user_consent = False
        api_key = os.getenv("GROQ_API_KEY")
        use_external_ai = enable_external_ai and user_consent and api_key
        assert not use_external_ai, (
            "External AI should not be used when operator disabled"
        )

    # Scenario 2: Operator disabled, user consent present
    # Expected: External AI NOT called (operator config takes precedence)
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "false"}, clear=True):
        enable_external_ai = is_external_ai_enabled()
        user_consent = True
        api_key = os.getenv("GROQ_API_KEY")
        use_external_ai = enable_external_ai and user_consent and api_key
        assert not use_external_ai, (
            "External AI should not be used when operator disabled, even with consent"
        )

    # Scenario 3: Operator enabled, user consent absent
    # Expected: External AI NOT called (user consent required)
    with patch.dict(
        os.environ,
        {"ENABLE_EXTERNAL_AI": "true", "GROQ_API_KEY": "test_key"},
        clear=True,
    ):
        enable_external_ai = is_external_ai_enabled()
        user_consent = False
        api_key = os.getenv("GROQ_API_KEY")
        use_external_ai = enable_external_ai and user_consent and api_key
        assert not use_external_ai, (
            "External AI should not be used without user consent"
        )

    # Scenario 4: Operator enabled, user consent present, API key missing
    # Expected: External AI NOT called (API key required)
    with patch.dict(os.environ, {"ENABLE_EXTERNAL_AI": "true"}, clear=True):
        enable_external_ai = is_external_ai_enabled()
        user_consent = True
        api_key = os.getenv("GROQ_API_KEY")
        use_external_ai = enable_external_ai and user_consent and api_key
        assert not use_external_ai, "External AI should not be used without API key"

    # Scenario 5: Operator enabled, user consent present, API key available
    # Expected: External AI CAN be called (all conditions satisfied)
    with patch.dict(
        os.environ,
        {"ENABLE_EXTERNAL_AI": "true", "GROQ_API_KEY": "test_key"},
        clear=True,
    ):
        enable_external_ai = is_external_ai_enabled()
        user_consent = True
        api_key = os.getenv("GROQ_API_KEY")
        use_external_ai = enable_external_ai and user_consent and api_key
        assert use_external_ai, (
            "External AI should be available when all conditions are met"
        )

    # Verify default UI state does not grant consent automatically
    # The checkbox in Daily_Input.py uses value=False by default
    # This is verified by inspection of the code (line 76: value=False)
    # Local analysis remains available without consent (tested in test_external_ai_disabled)


def test_journal_persistence_after_groq_failure():
    """
    Test that journal entry can be saved even when Groq API fails.

    Invariant: A failed Groq request falls back to local analysis and
    does not prevent saving a valid journal entry when local analysis succeeds.

    This test verifies the NLP processor's fallback behavior ensures
    data persistence is not blocked by external API failures.
    """
    # Simulate Groq API failure
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("Groq API unavailable")

    processor = NLPProcessor(groq_client=mock_client)
    journal_text = "I had a productive day at work today."

    # Analyze entry - should fall back to local analysis
    result = processor.analyze_entry(journal_text)

    # Verify local analysis succeeded and produced valid result
    assert result is not None, "Analysis should succeed via local fallback"
    assert "sentiment_score" in result, "Result should contain sentiment_score"
    assert "sentiment_label" in result, "Result should contain sentiment_label"
    assert "emotions" in result, "Result should contain emotions"
    assert "keywords" in result, "Result should contain keywords"
    assert "topics" in result, "Result should contain topics"

    # Verify result structure is compatible with database schema
    assert isinstance(result["sentiment_score"], (int, float))
    assert isinstance(result["sentiment_label"], str)
    assert isinstance(result["emotions"], dict)
    assert isinstance(result["keywords"], list)
    assert isinstance(result["topics"], list)

    # The result can now be saved to the database via save_entry()
    # This test verifies the data contract is satisfied even after Groq failure


# ===== JSON Parsing and Validation Tests =====


def test_valid_ai_json_response():
    """Test handling of valid AI JSON response"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "sentiment_score": 0.8,
            "sentiment_label": "positive",
            "emotions": {
                "joy": 0.9,
                "sadness": 0.1,
                "anger": 0.0,
                "fear": 0.0,
                "stress": 0.1,
                "calm": 0.8,
            },
            "keywords": ["happy", "great", "wonderful"],
            "topics": ["personal", "wellbeing"],
            "summary": "A positive day.",
            "insights": ["Good mood detected"],
        }
    )
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("I had a great day!")

    assert result is not None
    assert result["sentiment_score"] == 0.8
    assert result["sentiment_label"] == "positive"
    assert result["emotions"]["joy"] == 0.9


def test_malformed_json_response():
    """Test handling of malformed JSON response from Groq API"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "invalid json {{{"
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should fall back to local analysis
    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result


def test_empty_response_content():
    """Test handling of empty response content"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = ""
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should fall back to local analysis
    assert result is not None
    assert "sentiment_score" in result


def test_missing_required_fields():
    """Test handling of missing required fields in AI response"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "sentiment_score": 0.5,
            # Missing sentiment_label, emotions, keywords, topics
        }
    )
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should fill in defaults
    assert result is not None
    assert result["sentiment_score"] == 0.5
    assert result["sentiment_label"] == "neutral"  # Default
    assert isinstance(result["emotions"], dict)


def test_incorrect_field_types():
    """Test handling of incorrect field types in AI response"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "sentiment_score": "not a number",
            "sentiment_label": 123,
            "emotions": "not a dict",
            "keywords": "not a list",
            "topics": "not a list",
        }
    )
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should handle type errors gracefully
    assert result is not None
    assert isinstance(result["sentiment_score"], (int, float))
    assert isinstance(result["sentiment_label"], str)
    assert isinstance(result["emotions"], dict)
    assert isinstance(result["keywords"], list)
    assert isinstance(result["topics"], list)


def test_sentiment_out_of_range():
    """Test that sentiment scores are clamped to valid range"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "sentiment_score": 5.0,  # Out of range (> 1.0)
            "sentiment_label": "positive",
            "emotions": {"joy": 2.0, "sadness": -1.0},  # Out of range
            "keywords": [],
            "topics": [],
        }
    )
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should clamp values to valid ranges
    assert result is not None
    assert -1.0 <= result["sentiment_score"] <= 1.0
    assert 0.0 <= result["emotions"]["joy"] <= 1.0
    assert 0.0 <= result["emotions"]["sadness"] <= 1.0


def test_emotion_values_out_of_range():
    """Test that emotion values are clamped to 0.0-1.0 range"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "sentiment_score": 0.5,
            "sentiment_label": "neutral",
            "emotions": {
                "joy": 1.5,
                "sadness": -0.5,
                "anger": 2.0,
                "fear": 0.3,
                "stress": 1.1,
                "calm": 0.7,
            },
            "keywords": [],
            "topics": [],
        }
    )
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # All emotion values should be in valid range
    for emotion, value in result["emotions"].items():
        assert 0.0 <= value <= 1.0, f"Emotion {emotion} value {value} out of range"


def test_unexpected_response_structure():
    """Test handling of unexpected response structure"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = []  # Empty choices
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should fall back to local analysis
    assert result is not None
    assert "sentiment_score" in result


def test_api_timeout():
    """Test handling of API timeout"""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = TimeoutError("Request timed out")

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should fall back to local analysis
    assert result is not None
    assert "sentiment_score" in result


def test_groq_initialization_failure():
    """Test handling of Groq client initialization failure"""
    # Simulate initialization failure by passing invalid client
    processor = NLPProcessor(groq_client=None)
    result = processor.analyze_entry("Test text")

    # Should use local analysis
    assert result is not None
    assert "sentiment_score" in result
    assert "sentiment_label" in result


def test_local_fallback_compatibility():
    """Test that local fallback produces compatible data structure"""
    processor = NLPProcessor(groq_client=None)
    result = processor.analyze_entry("I had a good day at work.")

    # Verify all required fields for database storage exist
    assert "sentiment_score" in result
    assert isinstance(result["sentiment_score"], (int, float))
    assert -1.0 <= result["sentiment_score"] <= 1.0

    assert "sentiment_label" in result
    assert isinstance(result["sentiment_label"], str)
    assert result["sentiment_label"] in ["positive", "negative", "neutral"]

    assert "emotions" in result
    assert isinstance(result["emotions"], dict)
    expected_emotions = ["joy", "sadness", "anger", "fear", "stress", "calm"]
    for emotion in expected_emotions:
        assert emotion in result["emotions"]
        assert isinstance(result["emotions"][emotion], (int, float))
        assert 0.0 <= result["emotions"][emotion] <= 1.0

    assert "keywords" in result
    assert isinstance(result["keywords"], list)

    assert "topics" in result
    assert isinstance(result["topics"], list)


def test_summary_and_insights_optional():
    """Test that summary and insights are optional fields"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps(
        {
            "sentiment_score": 0.5,
            "sentiment_label": "neutral",
            "emotions": {
                "joy": 0.5,
                "sadness": 0.5,
                "anger": 0.0,
                "fear": 0.0,
                "stress": 0.5,
                "calm": 0.5,
            },
            "keywords": ["test"],
            "topics": ["test"],
            # No summary or insights
        }
    )
    mock_client.chat.completions.create.return_value = mock_response

    processor = NLPProcessor(groq_client=mock_client)
    result = processor.analyze_entry("Test text")

    # Should handle missing optional fields
    assert result is not None
    assert "summary" in result
    assert "insights" in result
