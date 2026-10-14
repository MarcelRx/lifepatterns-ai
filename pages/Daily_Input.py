# Daily Input Page
# -----------------------
import logging
from datetime import date

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import centralized configuration after loading .env
from utils.config import is_external_ai_enabled  # noqa: E402

# Configure logging
logger = logging.getLogger(__name__)


def show_page(user):
    """Display the daily input form for journal entries."""
    st.title("Daily Input")
    st.caption("Hello, " + user.username)

    # External AI must be enabled by the operator before consent is offered.
    enable_external_ai = is_external_ai_enabled()

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
        sleep = st.number_input(
            "Sleep Hours",
            min_value=0.0,
            max_value=12.0,
            value=7.0,
            step=0.5,
        )

    # Activities multi-select
    activities = st.multiselect(
        "Activities",
        [
            "Meditation",
            "Exercise",
            "Social",
            "Reading",
            "Work",
            "Sleep",
            "Family",
            "Walking",
            "Yoga",
            "Creative",
            "Nature",
            "Gaming",
            "Cooking",
        ],
    )

    # Journal text area
    journal = st.text_area("Journal Entry", height=150)

    # External AI consent is shown only when enabled by the operator.
    user_consent_external_ai = False

    if enable_external_ai:
        user_consent_external_ai = st.checkbox(
            "Enable AI-powered analysis (sends journal text to Groq API)",
            value=False,
            help=(
                "When enabled, your journal text will be sent to Groq for "
                "advanced AI analysis. Disable to use local analysis only."
            ),
        )

    # Both operator configuration and explicit user consent are required.
    use_external_ai = enable_external_ai and user_consent_external_ai

    if st.button("Save Entry", type="primary"):
        if not journal.strip():
            st.warning("Please write something")
            return

        with st.spinner("Analyzing..."):
            from models.nlp_processor import NLPProcessor

            # Crucially, do not let the processor auto-create a Groq client
            # unless both operator configuration and user consent are true.
            try:
                processor = NLPProcessor(
                    enable_external_ai=use_external_ai,
                )
            except Exception:
                # Fail closed: use local analysis if external client setup fails.
                logger.warning(
                    "NLP processor initialization failed. Retrying with local analysis."
                )
                processor = NLPProcessor()

            result = processor.analyze_entry(journal)

            from utils.database import save_entry

            # Summary and insights are display-only; they are not persisted
            # because they are not part of the current database schema.
            entry_data = {
                "user_id": user.id,
                "date": entry_date,
                "text": journal,
                "mood": mood,
                "energy": energy,
                "sleep": sleep,
                "activities": activities,
                "sentiment_score": result["sentiment_score"],
                "sentiment_label": result["sentiment_label"],
                "emotions": result["emotions"],
                "keywords": result["keywords"],
                "topics": result["topics"],
            }

            if save_entry(entry_data):
                st.success("Saved!")

                display_result = {
                    "sentiment_score": result["sentiment_score"],
                    "sentiment_label": result["sentiment_label"],
                    "emotions": result["emotions"],
                    "keywords": result["keywords"],
                    "topics": result["topics"],
                }

                if result.get("summary"):
                    display_result["summary"] = result["summary"]

                if result.get("insights"):
                    display_result["insights"] = result["insights"]

                st.json(display_result)
            else:
                st.error("Failed to save")


def main():
    """Standalone execution mode - shows an error message."""
    st.error("Run via app.py")


__all__ = ["show_page", "main"]
