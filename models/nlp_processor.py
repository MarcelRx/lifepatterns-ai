# NLP Processing for journal entries using Groq AI and local fallback
# -------------------------------------------------------------------
import os
import json
import re
from typing import Dict, List, Optional
from collections import Counter
from groq import Groq
from dotenv import load_dotenv

# Attempt to import TextBlob for local sentiment analysis (fallback option)
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

class NLPProcessor:
    """Process journal entries using AI-powered NLP with local fallback capabilities"""
    
    def __init__(self, groq_client: Optional[Groq] = None):
        """Initialize NLP processor with optional Groq client or create new one"""
        self.groq_client = groq_client or self._create_groq_client()
        
        # Emotion keywords dictionary for local sentiment analysis
        self.emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'fantastic', 'awesome', 'cheerful', 'delighted', 'grateful', 'blessed'],
            'sadness': ['sad', 'depressed', 'down', 'unhappy', 'miserable', 'disappointed', 'heartbroken', 'lonely', 'empty'],
            'anger': ['angry', 'mad', 'frustrated', 'annoyed', 'irritated', 'furious', 'hate', 'rage', 'stressed'],
            'fear': ['anxious', 'worried', 'scared', 'afraid', 'nervous', 'panic', 'overwhelmed', 'tense'],
            'stress': ['stress', 'pressure', 'burden', 'exhausted', 'burnout', 'tired', 'drained', 'overworked'],
            'calm': ['peaceful', 'calm', 'relaxed', 'serene', 'tranquil', 'mindful', 'centered', 'balanced']
        }
        
        # Activity keywords for topic detection
        self.activity_keywords = [
            'exercise', 'work', 'meeting', 'read', 'walk', 'meditation', 'yoga', 'run', 'gym',
            'family', 'friends', 'social', 'date', 'party', 'travel', 'drive', 'cook', 'eat',
            'sleep', 'nap', 'rest', 'movie', 'tv', 'game', 'study', 'learn', 'project',
            'shopping', 'clean', 'organize', 'nature', 'outdoor', 'music', 'art', 'write'
        ]
    
    def _create_groq_client(self) -> Optional[Groq]:
        """Create Groq client from environment variables, returns None if no API key"""
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            return Groq(api_key=api_key)
        return None
    
    def analyze_entry(self, text: str) -> Dict:
        """
        Analyze journal entry text and return comprehensive NLP results.
        Tries Groq AI first, falls back to local analysis if AI fails or unavailable.
        """
        # Check for empty input
        if not text or not text.strip():
            return self._empty_result()
        
        # Attempt AI-powered analysis first (if Groq client available)
        if self.groq_client:
            try:
                return self._ai_analyze(text)
            except Exception as e:
                # Log AI failure and fall back to local analysis
                print(f"AI analysis failed, using local fallback: {e}")
        
        # Fall back to local NLP analysis
        return self._local_analyze(text)
    
    def _ai_analyze(self, text: str) -> Dict:
        """Use Groq AI for advanced NLP analysis with structured output"""
        
        # Create detailed prompt for AI analysis
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
        
        # Send request to Groq API
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert NLP analyst specializing in emotional and behavioral analysis of personal journal entries."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # Force JSON output
            max_tokens=500,
            temperature=0.3  # Lower temperature for more consistent results
        )
        
        # Parse AI response
        result = json.loads(response.choices[0].message.content)
        
        # Ensure all required fields exist with fallback defaults
        return {
            "sentiment_score": result.get("sentiment_score", 0.0),
            "sentiment_label": result.get("sentiment_label", "neutral"),
            "emotions": result.get("emotions", self._default_emotions()),
            "keywords": result.get("keywords", []),
            "topics": result.get("topics", []),
            "summary": result.get("summary", ""),
            "insights": result.get("insights", [])
        }
    
    def _local_analyze(self, text: str) -> Dict:
        """Local NLP analysis using TextBlob (if available) and keyword matching"""
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Sentiment analysis (TextBlob if available, otherwise keyword-based)
        if TEXTBLOB_AVAILABLE:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # Range: -1.0 to 1.0
            subjectivity = blob.sentiment.subjectivity  # Range: 0.0 to 1.0
        else:
            # Simple keyword-based sentiment calculation
            polarity = self._calculate_sentiment(text_lower)
            subjectivity = 0.5  # Default subjectivity value
        
        # Emotion detection using keyword matching
        emotions = self._detect_emotions(text_lower)
        
        # Keyword extraction from text
        keywords = self._extract_keywords(text)
        
        # Topic detection based on content
        topics = self._detect_topics(text_lower)
        
        # Generate brief summary
        summary = self._generate_summary(text, polarity, emotions)
        
        # Return comprehensive analysis results
        return {
            "sentiment_score": round(polarity, 2),  # Round to 2 decimal places
            "sentiment_label": self._sentiment_label(polarity),
            "emotions": emotions,
            "keywords": keywords,
            "topics": topics,
            "summary": summary,
            "insights": self._generate_insights(emotions, polarity)
        }
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score using positive/negative word frequency"""
        
        # Positive sentiment keywords
        positive_words = ['good', 'great', 'happy', 'excellent', 'love', 'best', 'fantastic', 
                         'wonderful', 'amazing', 'joy', 'excited', 'grateful', 'blessed']
        
        # Negative sentiment keywords
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'sad', 'angry', 
                         'frustrated', 'disappointed', 'anxious', 'worried', 'stressed']
        
        # Count keyword occurrences
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        # Calculate normalized sentiment score (-1.0 to 1.0)
        total = pos_count + neg_count
        if total == 0:
            return 0.0  # Neutral sentiment
        return (pos_count - neg_count) / total
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions based on keyword matching and frequency"""
        
        emotions = {}
        for emotion, keywords in self.emotion_keywords.items():
            # Count occurrences of emotion keywords
            count = sum(1 for keyword in keywords if keyword in text)
            # Normalize to 0-1 scale (max 3 occurrences = 1.0)
            emotions[emotion] = min(count / 3, 1.0)
        return emotions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text using frequency analysis"""
        
        # Remove punctuation and extract words (4+ letters only)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'were', 'been', 'their', 'what', 'when', 'where', 'which', 'while', 'about', 'would', 'there', 'could', 'should'}
        words = [w for w in words if w not in stop_words]
        
        # Count word frequency and return most common words
        freq = Counter(words)
        return [word for word, count in freq.most_common(8)]  # Top 8 keywords
    
    def _detect_topics(self, text: str) -> List[str]:
        """Detect main topics based on activity and theme keywords"""
        
        topics = []
        
        # Topic keyword mapping
        topic_keywords = {
            'work': ['work', 'job', 'career', 'office', 'meeting', 'project', 'deadline', 'boss', 'colleague'],
            'relationships': ['family', 'friend', 'partner', 'wife', 'husband', 'girlfriend', 'boyfriend', 'date', 'love', 'relationship'],
            'health': ['exercise', 'workout', 'gym', 'run', 'walk', 'healthy', 'sick', 'doctor', 'medicine', 'diet'],
            'mental_health': ['anxiety', 'depression', 'therapy', 'meditation', 'mindful', 'stress', 'overwhelmed'],
            'leisure': ['movie', 'tv', 'game', 'read', 'book', 'hobby', 'fun', 'relax', 'weekend'],
            'sleep': ['sleep', 'tired', 'exhausted', 'rest', 'nap', 'insomnia', 'dream']
        }
        
        # Check each topic for keyword matches
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        # Return topics (max 4) or default topic
        return topics[:4] if topics else ['daily_life']
    
    def _generate_summary(self, text: str, sentiment: float, emotions: Dict) -> str:
        """Generate a brief summary of the journal entry"""
        
        # Identify dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else 'neutral'
        
        # Determine sentiment description
        sentiment_desc = "positive" if sentiment > 0.2 else "negative" if sentiment < -0.2 else "neutral"
        
        # Extract first sentence or first 100 characters
        first_sentence = text.split('.')[0][:100]
        
        return f"Entry describes a {sentiment_desc} day with dominant {dominant_emotion} tone. {first_sentence}."
    
    def _generate_insights(self, emotions: Dict, sentiment: float) -> List[str]:
        """Generate behavioral insights based on emotions and sentiment"""
        
        insights = []
        
        # Stress-related insight
        if emotions.get('stress', 0) > 0.5:
            insights.append("High stress levels detected - consider stress management techniques")
        
        # Positive emotion insight
        if emotions.get('joy', 0) > 0.5 and sentiment > 0.3:
            insights.append("Positive emotional state - good time for creative activities")
        
        # Sadness-related insight
        if emotions.get('sadness', 0) > 0.5:
            insights.append("Low mood detected - prioritize self-care and social connection")
        
        # Calmness insight
        if emotions.get('calm', 0) > 0.5:
            insights.append("Balanced emotional state - maintain current routines")
            
        # Default insight if none triggered
        return insights if insights else ["Continue tracking to identify patterns"]
    
    def _sentiment_label(self, score: float) -> str:
        """Convert sentiment score to descriptive label"""
        if score > 0.2:
            return "positive"
        elif score < -0.2:
            return "negative"
        return "neutral"
    
    def _default_emotions(self) -> Dict[str, float]:
        """Return default emotion scores (all zero)"""
        return {'joy': 0.0, 'sadness': 0.0, 'anger': 0.0, 'fear': 0.0, 'stress': 0.0, 'calm': 0.0}
    
    def _empty_result(self) -> Dict:
        """Return empty result structure for empty input"""
        return {
            "sentiment_score": 0.0,
            "sentiment_label": "neutral",
            "emotions": self._default_emotions(),
            "keywords": [],
            "topics": [],
            "summary": "",
            "insights": []
        }

# Convenience function for direct use without class instantiation
def analyze_text(text: str, groq_client: Optional[Groq] = None) -> Dict:
    """Quick function to analyze text without needing to instantiate NLPProcessor class"""
    processor = NLPProcessor(groq_client)
    return processor.analyze_entry(text)