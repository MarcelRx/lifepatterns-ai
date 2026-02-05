# Reports Page - Analytics and Data Visualization
# ---------------------------------------------------
import streamlit as st
from utils.database import get_entries, get_user_stats
from components.visualizations import Visualizations

def show_page(user):
    """Main page function - called by app.py with authenticated user"""
    
    # Page header with personalized caption
    st.title("Reports")
    st.caption(f"Analytics dashboard for {user.username}")
    
    # DATA RETRIEVAL 
    # Get user-specific entries with privacy protection (user_id filter)
    entries = get_entries(user_id=user.id)
    
    # EMPTY DATA CHECK 
    # Check if user has any data to display
    if not entries:
        st.info("No data to display yet.")
        st.write("Start adding daily entries to see your reports!")
        return
    
    # SUMMARY STATISTICS SECTION 
    st.markdown("### Summary Statistics")
    
    # Try to fetch and display user statistics
    try:
        stats = get_user_stats(user.id)
        
        # Create four-column layout for key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Entries", stats['total_entries'])
        with col2:
            st.metric("Avg Mood", f"{stats['avg_mood']}/10")
        with col3:
            st.metric("Avg Energy", f"{stats['avg_energy']}/10")
        with col4:
            st.metric("Avg Sleep", f"{stats['avg_sleep']}h")
    except:
        # Fallback message if statistics unavailable
        st.info("Calculating statistics...")
    
    # TIME PERIOD TABS SECTION 
    st.markdown("---")
    
    # Create tabbed interface for different time views
    tab1, tab2, tab3 = st.tabs(["Day", "Week", "Month"])
    
    # DAY VIEW TAB 
    with tab1:
        st.markdown("### Today's Summary")
        
        if entries:
            # Get latest entry (most recent)
            latest = entries[0]
            
            # Four-column layout for today's metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mood", f"{latest.mood_rating}/10")
            with col2:
                st.metric("Energy", f"{latest.energy_level}/10")
            with col3:
                st.metric("Sleep", f"{latest.sleep_hours}h")
            with col4:
                # Count activities if available
                activities_count = len(latest.activities) if latest.activities else 0
                st.metric("Activities", activities_count)
            
            # Display latest journal entry (truncated if long)
            if latest.journal_text:
                st.markdown("**Latest Journal Entry:**")
                st.info(latest.journal_text[:300] + "..." if len(latest.journal_text) > 300 else latest.journal_text)
            
            # Display sentiment analysis if available
            if latest.sentiment_score != 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Sentiment", latest.sentiment_label or "neutral")
                with col2:
                    st.metric("Score", f"{latest.sentiment_score:+.2f}")
    
    # WEEK VIEW TAB 
    with tab2:
        st.markdown("### Weekly Analysis (Last 7 Entries)")
        
        # Get last 7 entries for weekly view
        week_entries = entries[:7]
        
        # Initialize visualization engine with weekly data
        viz = Visualizations(week_entries)
        
        # Check if enough data for weekly analysis
        if len(week_entries) >= 2:
            # Mood trend chart (full width)
            mood_chart = viz.mood_trend_chart()
            if mood_chart:
                st.plotly_chart(mood_chart, use_container_width=True)
            
            # Two-column layout for secondary charts
            col1, col2 = st.columns(2)
            
            # Column 1: Activity impact chart
            with col1:
                activity_chart = viz.activity_impact_chart()
                if activity_chart:
                    st.plotly_chart(activity_chart, use_container_width=True)
            
            # Column 2: Sleep-mood correlation chart
            with col2:
                sleep_chart = viz.sleep_mood_correlation()
                if sleep_chart:
                    st.plotly_chart(sleep_chart, use_container_width=True)
        else:
            # Informational message if insufficient weekly data
            st.info("Add more entries for weekly charts")
    
    # MONTH VIEW TAB 
    with tab3:
        st.markdown("### Monthly Trends (Last 30 Entries)")
        
        # Get last 30 entries for monthly view
        month_entries = entries[:30]
        
        # Initialize visualization engine with monthly data
        viz = Visualizations(month_entries)
        
        # Check if enough data for monthly analysis
        if len(month_entries) >= 7:
            # Full mood trend chart
            mood_chart = viz.mood_trend_chart()
            if mood_chart:
                st.plotly_chart(mood_chart, use_container_width=True)
            
            # Weekly summary statistics
            weekly = viz.weekly_summary()
            if weekly:
                st.markdown("**Weekly Breakdown:**")
                
                # Create dynamic columns based on number of weeks
                cols = st.columns(min(len(weekly), 4))
                for i, week in enumerate(weekly):
                    with cols[i]:
                        st.metric(
                            week['week'], 
                            f"{week['avg_mood']}/10",
                            f"{week['entries']} entries"
                        )
                        st.caption(f"Energy: {week['avg_energy']}/10")
            
            # Sentiment timeline chart (if sentiment data available)
            sentiment_chart = viz.sentiment_timeline()
            if sentiment_chart:
                st.markdown("**Sentiment Timeline:**")
                st.plotly_chart(sentiment_chart, use_container_width=True)
        else:
            # Informational message if insufficient monthly data
            st.info(f"Add more entries for monthly view ({len(month_entries)}/7 minimum)")
    
    # DATA EXPORT SECTION 
    st.markdown("---")
    st.markdown("### Data Export")
    
    # Two-column layout for export options
    col1, col2 = st.columns(2)
    
    # Column 1: JSON export functionality
    with col1:
        if st.button("Export My Data (JSON)", use_container_width=True):
            import json
            from utils.database import get_all_entries_for_export
            
            # Fetch all user data for export
            data = get_all_entries_for_export(user.id)
            
            if data:
                # Convert data to JSON format
                json_str = json.dumps(data, indent=2, default=str)
                
                # Create download button
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"lifepatterns_data_{user.username}.json",
                    mime="application/json"
                )
            else:
                st.warning("No data to export")
    
    # Column 2: Data ownership reminder
    with col2:
        st.info("Your data belongs to you. Export anytime.")

def main():
    """Standalone execution mode - shows error message"""
    st.error("Access through main app")
    st.info("Run: `streamlit run app.py`")

# Application entry point for standalone testing
if __name__ == "__main__":
    main()