# Outcome Forecast Page - AI-Powered Future Predictions
# -----------------------------------------------------
import streamlit as st
from utils.database import get_entries
from models.pattern_detector import PatternDetector
from models.forecast_engine import ForecastEngine

def show_page(user):
    """Main page function - called by app.py for authenticated users"""
    
    # Page header with personalized caption
    st.title("Outcome Forecast")
    st.caption(f"Personal trajectory analysis for {user.username}")
    
    # DATA RETRIEVAL
    # Get user's journal entries from database
    entries = get_entries(user_id=user.id)
    
    # Check minimum data requirements for forecasting
    if len(entries) < 3:
        st.info("The crystal ball needs more data...")
        st.write("Add at least 3 entries to generate forecasts.")
        # Show progress indicator for data collection
        st.progress(len(entries) / 3, text=f"{len(entries)}/3 entries collected")
        return
    
    # PATTERN DETECTION 
    # Initialize pattern detector to identify behavior patterns
    detector = PatternDetector(entries)
    patterns = detector.get_all_patterns()
    
    # FORECAST ENGINE INITIALIZATION 
    # Attempt to initialize Groq client for AI-enhanced forecasting
    groq_client = None
    try:
        from groq import Groq
        import os
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            groq_client = Groq(api_key=api_key)
    except:
        # Silently continue without AI capabilities
        pass
    
    # Initialize forecast engine with entries, patterns, and optional AI client
    forecast_engine = ForecastEngine(entries, patterns, groq_client=groq_client)
    
    # Generate comprehensive wellbeing forecast
    forecast = forecast_engine.generate_forecast()
    
    # Validate forecast was successfully generated
    if not forecast:
        st.error("Unable to generate forecast. Please check your data.")
        return
    
    # CURRENT STATUS SECTION 
    status = forecast['current_status']
    
    st.markdown("### Current Wellbeing Status")
    
    # Define status indicators for visual feedback
    status_indicators = {
        "Thriving": "Thriving",    # Text for excellent wellbeing
        "Stable": "Stable",        # Text for stable state
        "Struggling": "Struggling",# Text for difficulties
        "Critical": "Critical"     # Text for critical state
    }
    
    # Get text indicator for current status
    status_indicator = status_indicators.get(status['status'], "Status")
    
    # Three-column layout for status metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", status_indicator)
    with col2:
        st.metric("Avg Mood", f"{status['avg_mood']}/10")
    with col3:
        st.metric("Avg Energy", f"{status['avg_energy']}/10")
    
    # Status assessment message
    st.info(status['assessment'])
    
    # TRAJECTORY SECTION 
    st.markdown("---")
    st.markdown("### Trajectory")
    
    traj = forecast['trajectory']
    direction = traj['direction']
    
    # Display trajectory with appropriate styling
    if direction == 'improving':
        st.success(f"""
        **Improving Trajectory**
        
        {traj['description']}
        **Change:** {traj['change']} | **Confidence:** {traj.get('confidence', 0):.0%}
        """)
        # Celebration animation for high-confidence improvements
        if traj.get('confidence', 0) > 0.7:
            st.balloons()
    elif direction == 'declining':
        st.error(f"""
        **Declining Trajectory**
        
        {traj['description']}
        **Change:** {traj['change']} | **Confidence:** {traj.get('confidence', 0):.0%}
        """)
        st.warning("Consider the interventions suggested below")
    else:
        st.info(f"""
        **Stable Trajectory**
        
        {traj['description']}
        **Confidence:** {traj.get('confidence', 0):.0%}
        """)
    
    # RISK ASSESSMENT SECTION 
    risks = forecast.get('risk_assessment', [])
    if risks:
        st.markdown("---")
        st.markdown("### Risk Assessment")
        
        # Display each risk with appropriate severity styling
        for risk in risks:
            level = risk['level']
            risk_type = risk['type'].replace('_', ' ').title()
            
            # High risk (red styling)
            if level == 'high':
                st.error(f"""
                **{risk_type}** (Probability: {risk['probability']})
                
                {risk['description']}
                """)
            # Medium risk (orange styling)
            elif level == 'medium':
                st.warning(f"""
                **{risk_type}** (Probability: {risk['probability']})
                
                {risk['description']}
                """)
            # Low risk (yellow styling)
            else:
                st.info(f"""
                **{risk_type}**
                
                {risk['description']}
                """)
    
    # 7-DAY MOOD FORECAST SECTION 
    st.markdown("---")
    st.markdown("### 7-Day Mood Forecast")
    
    pred = forecast['predictions']
    
    # Three-column layout for forecast metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current", f"{pred['current_mood']}/10")
    with col2:
        # Calculate mood change for delta display
        delta = pred['predicted_mood_7d'] - pred['current_mood']
        st.metric(
            "Predicted (7 days)", 
            f"{pred['predicted_mood_7d']}/10",
            delta=f"{delta:+.1f}",
            delta_color="normal" if delta >= 0 else "inverse"
        )
    with col3:
        outlook = pred['outlook']
        # Text-based outlook indicator
        outlook_text = outlook.title()
        st.metric("Outlook", outlook_text)
    
    # Daily prediction line chart
    st.markdown("**Daily Predictions:**")
    daily_predictions = pred.get('daily_predictions', [])
    if daily_predictions:
        # Prepare data for line chart
        chart_data = {d['date']: d['predicted_mood'] for d in daily_predictions}
        st.line_chart(chart_data)
        
        # Confidence disclaimer
        st.caption("Confidence decreases over time (starting at 90%)")
    
    # RECOMMENDED INTERVENTIONS SECTION 
    st.markdown("---")
    st.markdown("### Recommended Interventions")
    
    interventions = forecast.get('interventions', [])
    if interventions:
        # Display each intervention with urgency-based styling
        for i, intervention in enumerate(interventions, 1):
            with st.container():
                urgency = intervention['urgency']
                
                # Immediate interventions (red styling)
                if urgency == 'immediate':
                    st.error(f"""
                    **{i}. {intervention['action']}**
                    
                    **Impact:** {intervention['impact']}
                    **Evidence:** {intervention['evidence']}
                    """)
                # This-week interventions (orange styling)
                elif urgency == 'this_week':
                    st.warning(f"""
                    **{i}. {intervention['action']}**
                    
                    **Impact:** {intervention['impact']}
                    **Evidence:** {intervention['evidence']}
                    """)
                # Ongoing interventions (blue styling)
                else:
                    st.info(f"""
                    **{i}. {intervention['action']}**
                    
                    **Impact:** {intervention['impact']}
                    **Evidence:** {intervention['evidence']}
                    """)
    else:
        st.success("No interventions needed - keep up the good work!")
    
    # AI INSIGHTS SECTION 
    ai_insight = forecast.get('ai_insight')
    if ai_insight:
        st.markdown("---")
        st.markdown("### AI Generated Insight")
        
        # Extract AI insights
        key_insight = ai_insight.get('key_insight', '')
        watch_for = ai_insight.get('watch_for', '')
        opportunity = ai_insight.get('opportunity', '')
        
        # Display each insight with appropriate styling
        if key_insight:
            st.info(f"**Insight:** {key_insight}")
        if watch_for:
            st.warning(f"**Watch for:** {watch_for}")
        if opportunity:
            st.success(f"**Opportunity:** {opportunity}")

def main():
    """Standalone execution mode - shows error message"""
    st.error("Access this page through the main app")
    st.info("Run: `streamlit run app.py`")

# Application entry point for standalone testing
if __name__ == "__main__":
    main()