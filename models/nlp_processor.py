# NLP Processing for journal entries using Groq AI and local fallback
# -------------------------------------------------------------------
import json
import logging
import os
import re
from collections import Counter
from typing import Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq

# Attempt to import TextBlob for local sentiment analysis (fallback option)
try:
    from textblob import TextBlob

    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class NLPProcessor:
    """Process journal entries using external AI or local NLP analysis."""

    def __init__(
        self,
        groq_client: Optional[Groq] = None,
        enable_external_ai: bool = False,
    ):
        """
        Initialize the NLP processor.

        External AI is disabled by default. A Groq client is created from
        environment variables only when enable_external_ai=True.

        An explicitly injected client is accepted for dependency injection
        and testing. Callers must ensure that external AI use is authorized.
        """
        self.groq_client = groq_client

        if self.groq_client is None and enable_external_ai:
            self.groq_client = self._create_groq_client()

        # Emotion keywords dictionary for local sentiment analysis
        self.emotion_keywords = {
            "joy": [
                "happy",
                "joy",
                "excited",
                "great",
                "wonderful",
                "amazing",
                "love",
                "fantastic",
                "awesome",
                "cheerful",
                "delighted",
                "grateful",
                "blessed",
            ],
            "sadness": [
                "sad",
                "depressed",
                "down",
                "unhappy",
                "miserable",
                "disappointed",
                "heartbroken",
                "lonely",
                "empty",
            ],
            "anger": [
                "angry",
                "mad",
                "frustrated",
                "annoyed",
                "irritated",
                "furious",
                "hate",
                "rage",
                "stressed",
            ],
            "fear": [
                "anxious",
                "worried",
                "scared",
                "afraid",
                "nervous",
                "panic",
                "overwhelmed",
                "tense",
            ],
            "stress": [
                "stress",
                "pressure",
                "burden",
                "exhausted",
                "burnout",
                "tired",
                "drained",
                "overworked",
            ],
            "calm": [
                "peaceful",
                "calm",
                "relaxed",
                "serene",
                "tranquil",
                "mindful",
                "centered",
                "balanced",
            ],
        }

        # Activity keywords for topic detection
        self.activity_keywords = [
            "exercise",
            "work",
            "meeting",
            "read",
            "walk",
            "meditation",
            "yoga",
            "run",
            "gym",
            "family",
            "friends",
            "social",
            "date",
            "party",
            "travel",
            "drive",
            "cook",
            "eat",
            "sleep",
            "nap",
            "rest",
            "movie",
            "tv",
            "game",
            "study",
            "learn",
            "project",
            "shopping",
            "clean",
            "organize",
            "nature",
            "outdoor",
            "music",
            "art",
            "write",
        ]

    def _create_groq_client(self) -> Optional[Groq]:
        """Create a Groq client when explicitly enabled and an API key exists."""
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key or not api_key.strip():
            logger.info(
                "External AI is enabled, but no Groq API key is configured. "
                "Using local analysis."
            )
            return None

        try:
            return Groq(api_key=api_key.strip())
        except Exception:
            # Do not log exception details that could contain sensitive data.
            logger.warning("Groq client initialization failed. Using local analysis.")
            return None

    def analyze_entry(self, text: str) -> Dict:
        """
        Analyze a journal entry and return comprehensive NLP results.

        Uses Groq only when a client has explicitly been provided or created
        after external AI was enabled. Falls back to local analysis on failure.
        """
        if not text or not text.strip():
            return self._empty_result()

        if self.groq_client is not None:
            try:
                return self._ai_analyze(text)
            except (ValueError, json.JSONDecodeError):
                logger.warning("AI response validation failed. Using local fallback.")
            except Exception:
                # Avoid logging exception details that might contain
                # sensitive request or configuration information.
                logger.warning("AI analysis failed. Using local fallback.")

        return self._local_analyze(text)

    def _ai_analyze(self, text: str) -> Dict:
        """Use Groq AI for advanced NLP analysis with structured output."""
        prompt = f"""Analyze this journal entry comprehensively:

        Entry: "{text}"

        Provide detailed analysis in this exact JSON format:
        {{
            "sentiment_score": float (between -1.0 and 1.0),
            "sentiment_label": str ("positive", "negative", or "neutral"),
            "emotions": {{
                "joy": float (0.0 to 1.0),
                "sadness": float (0.0 to 1.0),
                "anger": float (0.0 to 1.0),
                "fear": float (0.0 to 1.0),
                "stress": float (0.0 to 1.0),
                "calm": float (0.0 to 1.0)
            }},
            "keywords": list of 5-10 important words or phrases,
            "topics": list of 3-5 main topics/themes,
            "summary": str (2-3 sentence summary),
            "insights": list of 2-3 behavioral insights
        }}

        Be accurate and nuanced in your analysis."""

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert NLP analyst specializing in "
                            "emotional and behavioral analysis of personal "
                            "journal entries."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.3,
            )

            if not response.choices or not response.choices[0].message:
                raise ValueError("Invalid AI response structure")

            content = response.choices[0].message.content

            if not content or not content.strip():
                raise ValueError("Empty AI response content")

            try:
                result = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON returned by AI") from exc

            if not isinstance(result, dict):
                raise ValueError("AI response must be a JSON object")

            return self._validate_ai_result(result)

        except (ValueError, json.JSONDecodeError):
            raise
        except Exception:
            logger.warning("Unexpected error during AI analysis.")
            raise

    def _validate_ai_result(self, result: Dict) -> Dict:
        """Validate and sanitize an AI response against the data contract."""
        if not isinstance(result, dict):
            raise ValueError("AI response must be a dictionary")

        validated = {}

        # Validate sentiment score
        sentiment_score = result.get("sentiment_score", 0.0)
        try:
            sentiment_score = float(sentiment_score)
            if not (
                sentiment_score == sentiment_score
                and abs(sentiment_score) != float("inf")
            ):
                sentiment_score = 0.0
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
        except (TypeError, ValueError, OverflowError):
            sentiment_score = 0.0

        validated["sentiment_score"] = sentiment_score

        # Validate sentiment label
        sentiment_label = result.get("sentiment_label", "neutral")
        if not isinstance(sentiment_label, str) or sentiment_label not in {
            "positive",
            "negative",
            "neutral",
        }:
            sentiment_label = "neutral"

        validated["sentiment_label"] = sentiment_label

        # Validate emotions
        emotions = result.get("emotions", {})
        if not isinstance(emotions, dict):
            emotions = {}

        validated_emotions = self._default_emotions()

        for emotion, value in emotions.items():
            if emotion not in validated_emotions:
                continue

            try:
                value = float(value)
                if not (value == value and abs(value) != float("inf")):
                    value = 0.0
                validated_emotions[emotion] = max(
                    0.0,
                    min(1.0, value),
                )
            except (TypeError, ValueError, OverflowError):
                validated_emotions[emotion] = 0.0

        validated["emotions"] = validated_emotions

        # Validate keywords
        keywords = result.get("keywords", [])
        if not isinstance(keywords, list):
            keywords = []

        validated["keywords"] = [
            str(item) for item in keywords if isinstance(item, (str, int, float))
        ][:10]

        # Validate topics
        topics = result.get("topics", [])
        if not isinstance(topics, list):
            topics = []

        validated["topics"] = [
            str(item) for item in topics if isinstance(item, (str, int, float))
        ][:5]

        # Validate summary
        summary = result.get("summary", "")
        validated["summary"] = summary[:500] if isinstance(summary, str) else ""

        # Validate insights
        insights = result.get("insights", [])
        if not isinstance(insights, list):
            insights = []

        validated["insights"] = [
            str(item) for item in insights if isinstance(item, (str, int, float))
        ][:3]

        return validated

    def _local_analyze(self, text: str) -> Dict:
        """Perform local NLP analysis using TextBlob and keyword matching."""
        text_lower = text.lower()

        if TEXTBLOB_AVAILABLE:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
        else:
            polarity = self._calculate_sentiment(text_lower)

        emotions = self._detect_emotions(text_lower)
        keywords = self._extract_keywords(text)
        topics = self._detect_topics(text_lower)
        summary = self._generate_summary(text, polarity, emotions)

        return {
            "sentiment_score": round(polarity, 2),
            "sentiment_label": self._sentiment_label(polarity),
            "emotions": emotions,
            "keywords": keywords,
            "topics": topics,
            "summary": summary,
            "insights": self._generate_insights(emotions, polarity),
        }

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment using positive and negative word frequency."""
        positive_words = [
            "good",
            "great",
            "happy",
            "excellent",
            "love",
            "best",
            "fantastic",
            "wonderful",
            "amazing",
            "joy",
            "excited",
            "grateful",
            "blessed",
        ]

        negative_words = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "worst",
            "sad",
            "angry",
            "frustrated",
            "disappointed",
            "anxious",
            "worried",
            "stressed",
        ]

        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)

        total = pos_count + neg_count

        if total == 0:
            return 0.0

        return (pos_count - neg_count) / total

    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions based on keyword matching."""
        emotions = {}

        for emotion, keywords in self.emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text)
            emotions[emotion] = min(count / 3, 1.0)

        return emotions

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract frequent keywords from the journal entry."""
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

        stop_words = {
            "this",
            "that",
            "with",
            "from",
            "they",
            "have",
            "were",
            "been",
            "their",
            "what",
            "when",
            "where",
            "which",
            "while",
            "about",
            "would",
            "there",
            "could",
            "should",
        }

        words = [word for word in words if word not in stop_words]
        frequencies = Counter(words)

        return [word for word, _count in frequencies.most_common(8)]

    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics based on activity and theme keywords."""
        topics = []

        topic_keywords = {
            "work": [
                "work",
                "job",
                "career",
                "office",
                "meeting",
                "project",
                "deadline",
                "boss",
                "colleague",
            ],
            "relationships": [
                "family",
                "friend",
                "partner",
                "wife",
                "husband",
                "girlfriend",
                "boyfriend",
                "date",
                "love",
                "relationship",
            ],
            "health": [
                "exercise",
                "workout",
                "gym",
                "run",
                "walk",
                "healthy",
                "sick",
                "doctor",
                "medicine",
                "diet",
            ],
            "mental_health": [
                "anxiety",
                "depression",
                "therapy",
                "meditation",
                "mindful",
                "stress",
                "overwhelmed",
            ],
            "leisure": [
                "movie",
                "tv",
                "game",
                "read",
                "book",
                "hobby",
                "fun",
                "relax",
                "weekend",
            ],
            "sleep": [
                "sleep",
                "tired",
                "exhausted",
                "rest",
                "nap",
                "insomnia",
                "dream",
            ],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)

        return topics[:4] if topics else ["daily_life"]

    def _generate_summary(
        self,
        text: str,
        sentiment: float,
        emotions: Dict,
    ) -> str:
        """Generate a brief summary of the journal entry."""
        dominant_emotion = (
            max(emotions.items(), key=lambda item: item[1])[0]
            if emotions
            else "neutral"
        )

        sentiment_desc = (
            "positive"
            if sentiment > 0.2
            else "negative"
            if sentiment < -0.2
            else "neutral"
        )

        first_sentence = text.split(".")[0][:100]

        return (
            f"Entry describes a {sentiment_desc} day with dominant "
            f"{dominant_emotion} tone. {first_sentence}."
        )

    def _generate_insights(
        self,
        emotions: Dict,
        sentiment: float,
    ) -> List[str]:
        """Generate behavioral insights from detected emotions and sentiment."""
        insights = []

        if emotions.get("stress", 0) > 0.5:
            insights.append(
                "High stress levels detected - consider stress management techniques"
            )

        if emotions.get("joy", 0) > 0.5 and sentiment > 0.3:
            insights.append(
                "Positive emotional state - good time for creative activities"
            )

        if emotions.get("sadness", 0) > 0.5:
            insights.append(
                "Low mood detected - prioritize self-care and social connection"
            )

        if emotions.get("calm", 0) > 0.5:
            insights.append("Balanced emotional state - maintain current routines")

        return insights if insights else ["Continue tracking to identify patterns"]

    def _sentiment_label(self, score: float) -> str:
        """Convert sentiment score to a descriptive label."""
        if score > 0.2:
            return "positive"
        if score < -0.2:
            return "negative"
        return "neutral"

    def _default_emotions(self) -> Dict[str, float]:
        """Return default emotion scores."""
        return {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "stress": 0.0,
            "calm": 0.0,
        }

    def _empty_result(self) -> Dict:
        """Return an empty result structure for empty input."""
        return {
            "sentiment_score": 0.0,
            "sentiment_label": "neutral",
            "emotions": self._default_emotions(),
            "keywords": [],
            "topics": [],
            "summary": "",
            "insights": [],
        }


def analyze_text(
    text: str,
    groq_client: Optional[Groq] = None,
    enable_external_ai: bool = False,
) -> Dict:
    """
    Convenience function for analyzing text.

    Local analysis is the default. External AI must be explicitly enabled
    or supplied through an explicitly injected client.
    """
    processor = NLPProcessor(
        groq_client=groq_client,
        enable_external_ai=enable_external_ai,
    )
    return processor.analyze_entry(text)
