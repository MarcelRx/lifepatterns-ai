# Pattern Discovery Page - Discover Your Behavioral Patterns
# -----------------------------------------------------------
import streamlit as st
from utils.database import get_entries
from models.pattern_detector import PatternDetector
from components.visualizations import Visualizations

def show_page(user):
    """Main page function - called by app.py with authenticated user object"""
    
    # Page header with personalized caption
    st.title("Pattern Discovery")
    st.caption(f"Exploring patterns for {user.username}")
    
    # DATA RETRIEVAL 
    # Get user-specific entries with privacy protection (user_id filter)
    entries = get_entries(user_id=user.id)
    
    # MINIMUM DATA CHECK 
    # Require at least 3 entries for meaningful pattern detection
    if len(entries) < 3:
        st.info("Need at least 3 entries to detect patterns.")
        st.write("Keep adding daily entries and check back here!")
        
        # Show progress indicator to motivate continued tracking
        st.progress(len(entries) / 3, text=f"Progress: {len(entries)}/3 entries")
        return
    
    # TODAY'S VIBE SECTION 
    st.markdown("### Today's Vibe")
    
    # Create two-column layout for vibe assessment
    col1, col2 = st.columns(2)
    
    # Get latest mood and energy ratings (most recent entry)
    recent_mood = entries[0].mood_rating if entries else 5
    recent_energy = entries[0].energy_level if entries else 5
    
    # Column 1: Vibe description based on mood level
    with col1:
        if recent_mood >= 7:
            st.success("""
            **Creative Flow**
            
            You are in a high energy creative peak today. Perfect time for brainstorming and deep work.
            """)
        elif recent_mood >= 5:
            st.info("""
            **Balanced State**
            
            You're in good equilibrium. Great for routine tasks and steady progress.
            """)
        else:
            st.warning("""
            **Low Energy**
            
            Take it easy today. Focus on self-care and rest. Tomorrow is a new day.
            """)
    
    # Column 2: Quantitative metrics with progress bars
    with col2:
        st.metric("Current Mood", f"{recent_mood}/10")
        st.progress(recent_mood / 10)  # Convert to 0-1 scale for progress bar
        
        st.metric("Current Energy", f"{recent_energy}/10")
        st.progress(recent_energy / 10)  # Convert to 0-1 scale for progress bar
    
    # VISUALIZATIONS SECTION 
    st.markdown("---")
    st.markdown("### Your Trends")
    
    # Initialize visualization engine with user entries
    viz = Visualizations(entries)
    
    # Mood trend chart (full width)
    mood_chart = viz.mood_trend_chart()
    if mood_chart:
        st.plotly_chart(mood_chart, use_container_width=True)
    else:
        st.info("Add more entries to see mood trends")
    
    # Two-column layout for secondary charts
    col1, col2 = st.columns(2)
    
    # Column 1: Activity impact visualization
    with col1:
        activity_chart = viz.activity_impact_chart()
        if activity_chart:
            st.plotly_chart(activity_chart, use_container_width=True)
        else:
            st.info("Add activities to see impact")
    
    # Column 2: Sleep-mood correlation visualization
    with col2:
        sleep_chart = viz.sleep_mood_correlation()
        if sleep_chart:
            st.plotly_chart(sleep_chart, use_container_width=True)
        else:
            st.info("Add sleep data for correlation")
    
    # AI PATTERN DETECTION SECTION 
    st.markdown("---")
    st.markdown("### AI Detected Patterns")
    
    # Initialize pattern detector with user entries
    detector = PatternDetector(entries)
    
    # Run pattern detection algorithms
    patterns = detector.get_all_patterns()
    
    # Display detected patterns or informational message
    if patterns:
        for pattern in patterns:
            display_pattern(pattern)
    else:
        st.info("No significant patterns detected yet.")
        st.caption("Keep logging daily - patterns emerge with more data!")

def display_pattern(pattern):
    """Display a single pattern card with styling and visualization"""
    
    # Pattern type indicators for visual identification (text-based)
    pattern_indicators = {
        "mood_trend": "MT",               # Text indicator for mood trends
        "sleep_mood_correlation": "SM",   # Text indicator for sleep patterns
        "activity_impact": "AI",          # Text indicator for activity patterns
        "energy_pattern": "EP"            # Text indicator for energy patterns
    }
    
    # Select appropriate indicator based on pattern type
    indicator = pattern_indicators.get(pattern.get('type'), "[PATTERN]")  # Default pattern indicator
    
    # Create container for each pattern
    with st.container():
        # Two-column layout: indicator and content
        col1, col2 = st.columns([1, 6])
        
        # Column 1: Pattern type indicator
        with col1:
            st.markdown(f"### {indicator}")
        
        # Column 2: Pattern details
        with col2:
            # Pattern name as subheader
            st.subheader(pattern.get('name', 'Unknown Pattern'))
            
            # Pattern description
            st.write(pattern.get('description', ''))
            
            # Confidence visualization with progress bar
            confidence = pattern.get('confidence', 0.5)
            st.progress(confidence, text=f"Confidence: {confidence:.0%}")
            
            # Display insight if available
            insight = pattern.get('insight')
            if insight:
                st.success(f"{insight}")
            
            # Trend-specific feedback for mood trends
            if pattern.get('type') == 'mood_trend':
                trend = pattern.get('trend')
                change = pattern.get('change', '0')
                
                # Positive feedback for improving trends
                if trend == 'improving':
                    st.success(f"Trending up by {change}!")
                
                # Warning for declining trends
                elif trend == 'declining':
                    st.warning(f"Trending down by {change} - consider self-care")
        
        # Visual divider between patterns
        st.divider()

# BACKWARD COMPATIBILITY 
def main():
    """Standalone execution mode - shows error message"""
    st.error("Please access this page through the main app")
    st.info("Run: `streamlit run app.py`")

# Application entry point for standalone testing
if __name__ == "__main__":
    main()