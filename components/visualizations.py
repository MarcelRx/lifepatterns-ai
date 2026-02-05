# Advanced visualizations for LifePatterns AI
# --------------------------------------------
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from collections import defaultdict

class Visualizations:
    """Create interactive charts and graphs for the LifePatterns AI dashboard"""
    
    def __init__(self, entries):
        # Initialize with user entries and prepare DataFrame
        self.entries = entries
        self.df = self._prepare_dataframe()
    
    def _prepare_dataframe(self):
        """Convert entry objects to pandas DataFrame for analysis"""
        
        # Return empty DataFrame if no entries
        if not self.entries:
            return pd.DataFrame()
        
        # Extract data from each entry object
        data = []
        for e in self.entries:
            data.append({
                'date': e.entry_date,
                'mood': e.mood_rating,
                'energy': e.energy_level,
                'sleep': e.sleep_hours,
                'activities': e.activities or [],  # Ensure activities is a list
                'sentiment': getattr(e, 'sentiment_score', 0)  # Get sentiment if available
            })
        
        # Create DataFrame and sort by date
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        return df
    
    def mood_trend_chart(self):
        """Create interactive line chart showing mood and energy trends over time"""
        
        # Check if sufficient data exists
        if self.df.empty or len(self.df) < 2:
            return None
        
        # Initialize Plotly figure
        fig = go.Figure()
        
        # Add mood line with area fill
        fig.add_trace(go.Scatter(
            x=self.df['date'],
            y=self.df['mood'],
            mode='lines+markers',
            name='Mood',
            line=dict(color='#2196F3', width=3),  # Blue line
            marker=dict(size=8, color='#2196F3'),
            fill='tozeroy',  # Fill area below line
            fillcolor='rgba(33, 150, 243, 0.1)'  # Semi-transparent blue
        ))
        
        # Add energy line
        fig.add_trace(go.Scatter(
            x=self.df['date'],
            y=self.df['energy'],
            mode='lines+markers',
            name='Energy',
            line=dict(color='#4CAF50', width=3),  # Green line
            marker=dict(size=8, color='#4CAF50')
        ))
        
        # Add rolling average trend line (if sufficient data)
        if len(self.df) >= 3:
            z = pd.Series(self.df['mood']).rolling(window=3, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=self.df['date'],
                y=z,
                mode='lines',
                name='Trend',
                line=dict(color='#FF9800', width=2, dash='dash')  # Orange dashed line
            ))
        
        # Configure chart layout
        fig.update_layout(
            title='Mood & Energy Trends',
            xaxis_title='Date',
            yaxis_title='Rating (1-10)',
            yaxis=dict(range=[0, 10]),  # Fixed y-axis scale
            template='plotly_dark',  # Dark theme
            height=400,
            hovermode='x unified'  # Show all data at same x position
        )
        
        return fig
    
    def activity_impact_chart(self):
        """Create bar chart showing average mood for each activity"""
        
        # Check if data exists
        if self.df.empty:
            return None
        
        # Calculate average mood by activity
        activity_moods = defaultdict(list)
        
        # Group moods by activity
        for _, row in self.df.iterrows():
            if row['activities'] and row['mood']:
                for activity in row['activities']:
                    activity_moods[activity].append(row['mood'])
        
        # Return None if no activity data
        if not activity_moods:
            return None
        
        # Prepare data for chart
        activities = []
        avg_moods = []
        counts = []
        
        for activity, moods in activity_moods.items():
            if len(moods) >= 1:  # Require at least 1 data point
                activities.append(activity)
                avg_moods.append(sum(moods) / len(moods))
                counts.append(len(moods))
        
        # Return None if no valid activities
        if not activities:
            return None
        
        # Sort activities by average mood (highest first)
        sorted_data = sorted(zip(activities, avg_moods, counts), key=lambda x: x[1], reverse=True)
        activities, avg_moods, counts = zip(*sorted_data)
        
        # Color code bars based on mood score
        colors = ['#4CAF50' if m >= 7 else '#FFC107' if m >= 5 else '#F44336' for m in avg_moods]
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=activities,
                y=avg_moods,
                marker_color=colors,
                text=[f'{m:.1f}<br>(n={c})' for m, c in zip(avg_moods, counts)],  # Show count
                textposition='auto'
            )
        ])
        
        # Configure chart layout
        fig.update_layout(
            title='Activity Impact on Mood',
            xaxis_title='Activity',
            yaxis_title='Average Mood',
            yaxis=dict(range=[0, 10]),  # Fixed y-axis scale
            template='plotly_dark',
            height=350
        )
        
        return fig
    
    def sleep_mood_correlation(self):
        """Create scatter plot showing relationship between sleep and mood"""
        
        # Check if data exists
        if self.df.empty:
            return None
        
        # Filter entries with both sleep and mood data
        df_valid = self.df[(self.df['sleep'].notna()) & (self.df['mood'].notna())]
        
        # Require minimum 3 data points
        if len(df_valid) < 3:
            return None
        
        # Create scatter plot with trend line
        fig = px.scatter(
            df_valid,
            x='sleep',
            y='mood',
            trendline='ols',  # Ordinary Least Squares trend line
            title='Sleep vs Mood Correlation',
            labels={'sleep': 'Sleep Hours', 'mood': 'Mood Rating'},
            template='plotly_dark',
            height=350
        )
        
        # Customize scatter points
        fig.update_traces(
            marker=dict(size=12, color='#2196F3', opacity=0.7),
            selector=dict(mode='markers')
        )
        
        # Set axis ranges
        fig.update_layout(
            xaxis=dict(range=[0, 12]),  # Sleep hours range
            yaxis=dict(range=[0, 10])   # Mood rating range
        )
        
        return fig
    
    def weekly_summary(self):
        """Calculate weekly summary statistics for display"""
        
        # Check if data exists
        if self.df.empty:
            return None
        
        # Add week number to DataFrame
        self.df['week'] = self.df['date'].dt.isocalendar().week
        
        weekly_stats = []
        for week, group in self.df.groupby('week'):
            stats = {
                'week': f"Week {week}",
                'avg_mood': round(group['mood'].mean(), 1),
                'avg_energy': round(group['energy'].mean(), 1),
                'avg_sleep': round(group['sleep'].mean(), 1) if group['sleep'].notna().any() else 0,
                'entries': len(group)
            }
            weekly_stats.append(stats)
        
        # Return statistics for last 4 weeks
        return weekly_stats[-4:]
    
    def sentiment_timeline(self):
        """Create timeline chart of AI sentiment scores"""
        
        # Check if sentiment data exists
        if self.df.empty or 'sentiment' not in self.df.columns:
            return None
        
        # Filter entries with sentiment scores
        df_sentiment = self.df[self.df['sentiment'] != 0]
        
        # Require minimum 2 data points
        if len(df_sentiment) < 2:
            return None
        
        # Create sentiment timeline chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_sentiment['date'],
            y=df_sentiment['sentiment'],
            mode='lines+markers',
            name='Sentiment',
            line=dict(color='#9C27B0', width=3),  # Purple line
            marker=dict(size=8)
        ))
        
        # Add reference lines for sentiment interpretation
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
        fig.add_hline(y=0.5, line_dash="dot", line_color="green", annotation_text="Positive")
        fig.add_hline(y=-0.5, line_dash="dot", line_color="red", annotation_text="Negative")
        
        # Configure chart layout
        fig.update_layout(
            title='AI Sentiment Analysis Over Time',
            xaxis_title='Date',
            yaxis_title='Sentiment Score (-1 to +1)',
            yaxis=dict(range=[-1, 1]),  # Sentiment range
            template='plotly_dark',
            height=300
        )
        
        return fig