# Import required libraries
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="LifePatterns AI",
    layout="centered"
)

# Display main title and subtitle
st.title("LifePatterns AI")
st.subheader("Personal Behavior & Outcome Analytics")

# Create sidebar for system status
st.sidebar.header("System Status")

# Test database connection
try:
    from data.database import test_connection
    db_ok = test_connection()
    st.sidebar.success("Database Connected")
except Exception as e:
    st.sidebar.error(f"Database Error: {e}")

# Add separator in sidebar
st.sidebar.markdown("---")

# Test Groq API connection
try:
    from models.groq_client import test_groq
    groq_ok = test_groq()
    st.sidebar.success("Groq API Connected")
except Exception as e:
    st.sidebar.error(f"Groq Error: {e}")

# Add separator in main content
st.markdown("---")

# Create daily input form section
st.header("Daily Entry")

# Create form for daily entries
with st.form("daily_entry"):
    # Create two columns for form layout
    col1, col2 = st.columns(2)
    
    # Left column inputs
    with col1:
        mood = st.slider("Mood (1-10)", 1, 10, 5)
        energy = st.slider("Energy (1-10)", 1, 10, 5)
    
    # Right column inputs
    with col2:
        sleep = st.number_input("Sleep hours", 0.0, 12.0, 7.0, 0.5)
        activities = st.multiselect(
            "Activities",
            ["Exercise", "Work", "Social", "Reading", "Meditation", "Gaming"]
        )
    
    # Journal text area
    journal = st.text_area(
        "Journal Entry",
        placeholder="How was your day? Write your thoughts here..."
    )
    
    # Submit button
    submitted = st.form_submit_button("Save Entry", use_container_width=True)
    
    # Handle form submission
    if submitted:
        st.success("Entry saved! (Test mode - not actually saving yet)")
        st.balloons()

# Add footer separator
st.markdown("---")
st.caption("LifePatterns AI")