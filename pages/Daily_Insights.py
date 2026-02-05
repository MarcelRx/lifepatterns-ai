# Daily Insights Page - Smart Recommendations
# --------------------------------------------
import streamlit as st
from utils.database import get_entries
from models.pattern_detector import PatternDetector
from models.recommendation_engine import RecommendationEngine

def show_page(user):
    """Main page function - called by app.py for authenticated users"""
    
    # Page header with personalization
    st.title("Daily Insights")
    st.caption(f"Personalized recommendations for {user.username}")
    
    # DATA RETRIEVAL 
    # Get user's journal entries from database
    entries = get_entries(user_id=user.id)
    
    # Check if enough data exists for analysis
    if len(entries) < 2:
        st.info("Add more entries to get personalized insights!")
        st.write("We need at least 2 entries to generate meaningful recommendations.")
        return
    
    # PATTERN DETECTION 
    # Initialize pattern detector with user entries
    detector = PatternDetector(entries)
    
    # Detect behavioral patterns from entries
    patterns = detector.get_all_patterns()
    
    # AI RECOMMENDATION ENGINE 
    # Attempt to initialize Groq client for AI-powered recommendations
    groq_client = None
    try:
        from groq import Groq
        import os
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            groq_client = Groq(api_key=api_key)
    except:
        # Silently continue if Groq unavailable (rule-based recommendations only)
        pass
    
    # Initialize recommendation engine with patterns, entries, and optional AI client
    rec_engine = RecommendationEngine(patterns, entries, groq_client=groq_client)
    
    # Generate personalized recommendations
    recommendations = rec_engine.generate_recommendations()
    
    # FEATURED INSIGHT SECTION 
    st.markdown("### Featured Insight")
    
    # Get latest entry for contextual insight
    latest = entries[0]
    mood = latest.mood_rating
    
    # Display mood-based contextual message
    if mood >= 7:
        st.success("""
        **You're on a roll!**
        
        Your recent entries show high wellbeing. This is a great time to:
        - Tackle challenging projects
        - Connect with friends and family
        - Establish new positive habits
        """)
    elif mood >= 5:
        st.info("""
        **Steady and balanced**
        
        You're maintaining a good equilibrium. Focus on:
        - Consistent routines
        - Small daily improvements
        - Mindfulness practices
        """)
    else:
        st.warning("""
        **Gentle care needed**
        
        Your recent mood is lower. Prioritize:
        - Adequate rest and sleep
        - Light physical activity
        - Connection with supportive people
        """)
    
    # PERSONALIZED RECOMMENDATIONS SECTION 
    st.markdown("---")
    st.markdown("### Personalized Recommendations")
    
    # Display recommendations if available
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            display_recommendation(i, rec)
    else:
        st.info("Keep logging your daily entries to receive AI-powered recommendations!")
    
    # QUICK ACTIONS SECTION 
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    # Create three-column layout for quick action buttons
    col1, col2, col3 = st.columns(3)
    
    # Quick Action 1: Meditation
    with col1:
        if st.button("5-min Meditation", use_container_width=True):
            st.success("Great choice! Even 5 minutes can reduce stress by 20%.")
    
    # Quick Action 2: Walking
    with col2:
        if st.button("Short Walk", use_container_width=True):
            st.success("Walking boosts mood and creativity. Enjoy!")
    
    # Quick Action 3: Gratitude Journal
    with col3:
        if st.button("Gratitude Journal", use_container_width=True):
            st.success("Write 3 things you're grateful for. It works!")
    
    # WEEKLY CHALLENGE SECTION 
    st.markdown("---")
    st.markdown("### Weekly Challenge")
    
    # Define weekly challenge options
    challenges = [
        "Log your mood every day for 7 days",
        "Get 7+ hours of sleep 5 nights this week",
        "Add 'Exercise' to your activities 3 times",
        "Write at least 100 words in your journal daily"
    ]
    
    # Select consistent challenge for each user (deterministic hash)
    challenge_index = hash(user.username) % len(challenges)
    challenge = challenges[challenge_index]
    
    # Display challenge with progress bar
    st.info(f"**This week's challenge:** {challenge}")
    st.progress(0.3, text="Progress: 2/7 days completed")

def display_recommendation(index, rec):
    """Display a single recommendation card with styling"""
    
    # Extract recommendation properties with defaults
    priority = rec.get('priority', 'medium')
    source = rec.get('source', 'rule-based')
    
    # Create container for each recommendation
    with st.container():
        # Two-column layout: priority indicator and content
        col1, col2 = st.columns([1, 8])
        
        # Column 1: Priority indicator (colored emoji)
        with col1:
            priority_emojis = {
                "high": "🔴",    # Red circle for high priority
                "medium": "🟠",  # Orange circle for medium priority
                "low": "🟢"      # Green circle for low priority
            }
            st.markdown(f"### {priority_emojis.get(priority, '⚪')}")
        
        # Column 2: Recommendation content
        with col2:
            # Title with optional AI badge
            title = rec.get('title', 'Recommendation')
            if source == 'AI':
                st.markdown(f"**{index}. {title}** AI`")
            else:
                st.markdown(f"**{index}. {title}**")
            
            # Description text
            st.write(rec.get('description', ''))
            
            # Action step (if provided)
            action = rec.get('action')
            if action:
                st.caption(f"**Action:** {action}")
            
            # Expected impact (if provided)
            impact = rec.get('expected_impact')
            if impact:
                st.caption(f"**Expected Impact:** {impact}")
            
            # Confidence score with progress bar visualization
            confidence = rec.get('confidence', 0.7)
            st.progress(confidence, text=f"Confidence: {confidence:.0%}")
        
        # Visual divider between recommendations
        st.divider()

def main():
    """Standalone execution mode - shows error message"""
    st.error("Access through main app")
    st.info("Run: `streamlit run app.py`")

# Application entry point for standalone testing
if __name__ == "__main__":
    main()