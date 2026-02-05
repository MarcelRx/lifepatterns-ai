# Daily Input Page
# -----------------------
import streamlit as st
import json
import os
import re
from datetime import date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# This function MUST be available for the main app to call
def show_page(user):
    """Display the daily input form for journal entries"""
    
    # Page header with user personalization
    st.title("Daily Input")
    st.caption("Hello, " + user.username)

    # Initialize Groq client if API key is available
    api_key = os.getenv("GROQ_API_KEY")
    groq_client = None
    if api_key:
        try:
            from groq import Groq
            groq_client = Groq(api_key=api_key)
        except:
            # Silently fail if Groq import fails
            pass

    # FORM LAYOUT
    # First row: Date and Mood
    col1, col2 = st.columns(2)
    with col1:
        entry_date = st.date_input("Date", date.today())
    with col2:
        mood = st.slider("Mood", 1, 10, 5)

    # Second row: Energy and Sleep
    col1, col2 = st.columns(2)
    with col1:
        energy = st.slider("Energy", 1, 10, 5)
    with col2:
        sleep = st.number_input("Sleep Hours", 0.0, 12.0, 7.0, 0.5)

    # Activities multi-select
    activities = st.multiselect(
        "Activities",
        ["Meditation", "Exercise", "Social", "Reading", "Work", "Sleep", "Family", 
         "Walking", "Yoga", "Creative", "Nature", "Gaming", "Cooking"]
    )

    # Journal text area
    journal = st.text_area("Journal Entry", height=150)

    # Save button with primary styling
    if st.button("Save Entry", type="primary"):
        # Validate journal entry is not empty
        if not journal.strip():
            st.warning("Please write something")
            return

        # Show loading spinner during analysis
        with st.spinner("Analyzing..."):
            # Perform text analysis
            result = analyze_text(journal)

            # Import database function
            from utils.database import save_entry

            # Prepare data for database storage
            entry_data = {
                "user_id": user.id,  # User ID for data isolation
                "date": entry_date,  # Entry date
                "text": journal,     # Journal text content
                "mood": mood,        # Mood rating (1-10)
                "energy": energy,    # Energy rating (1-10)
                "sleep": sleep,      # Sleep hours
                "activities": activities,  # Selected activities
                "sentiment_score": result["score"],  # Sentiment score
                "sentiment_label": result["label"],  # Sentiment label
                "emotions": json.dumps(result["emotions"]),  # JSON string of emotions
                "keywords": result["keywords"],      # Extracted keywords
                "topics": result["topics"]           # Detected topics
            }

            # Attempt to save to database
            if save_entry(entry_data):
                st.success("Saved!")
                # Display analysis results as JSON for debugging/verification
                st.json(result)
            else:
                st.error("Failed to save")

def analyze_text(text):
    """Analyze text for sentiment, emotions, keywords, and topics"""
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()

    # Define positive and negative sentiment keywords
    pos_words = ["happy", "good", "great", "love", "excellent", "joy", "excited", "grateful"]
    neg_words = ["sad", "bad", "terrible", "hate", "awful", "angry", "stressed", "anxious"]

    # Count positive and negative keyword occurrences
    pos = sum(1 for w in pos_words if w in text_lower)
    neg = sum(1 for w in neg_words if w in text_lower)

    # Calculate sentiment score
    total = pos + neg
    score = (pos - neg) / total if total > 0 else 0
    
    # Determine sentiment label based on score thresholds
    label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"

    # Calculate emotion scores based on keyword presence
    emotions = {
        "joy": min(pos / 3, 1.0),  # Joy based on positive word count
        "sadness": 1.0 if "sad" in text_lower else 0.0,
        "anger": 1.0 if "angry" in text_lower else 0.0,
        "fear": 1.0 if "afraid" in text_lower else 0.0,
        "stress": 1.0 if "stress" in text_lower else 0.0,
        "calm": 1.0 if "calm" in text_lower else 0.0
    }

    # Extract keywords from text
    words = re.findall(r"[a-zA-Z]{4,}", text_lower)  # Words with 4+ letters
    
    # Common stop words to filter out
    stops = {"this", "that", "with", "from", "they", "have", "were"}
    
    # Filter stop words and limit to top 6 keywords
    keywords = [w for w in words if w not in stops][:6]

    # Detect topics based on keyword presence
    topics = []
    if any(w in text_lower for w in ["work", "job"]):
        topics.append("work")
    elif any(w in text_lower for w in ["family", "friend"]):
        topics.append("relationships")
    else:
        topics.append("daily")

    # Return comprehensive analysis results
    return {
        "score": round(score, 2),  # Rounded sentiment score
        "label": label,            # Sentiment label
        "emotions": emotions,      # Emotion scores
        "keywords": keywords,      # Extracted keywords
        "topics": topics           # Detected topics
    }

def main():
    """Standalone execution mode - shows error message"""
    st.error("Run via app.py")

# Make show_page available at module level for import
__all__ = ["show_page", "main", "analyze_text"]