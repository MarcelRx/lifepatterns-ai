<<<<<<< Updated upstream
=======
# Pattern detection from journal entries
# ---------------------------------------
import json
from datetime import datetime, timedelta
from collections import defaultdict

class PatternDetector:
    """Detect behavioral patterns from daily journal entries"""
    
    def __init__(self, entries):
        # Initialize with list of database entry objects
        self.entries = entries
    
    def detect_mood_trend(self):
        """Detect overall mood trend: improving, declining, or stable"""
        
        # Require minimum 3 entries for trend analysis
        if len(self.entries) < 3:
            return None
        
        # Extract mood ratings from entries
        moods = [e.mood_rating for e in self.entries if e.mood_rating]
        if len(moods) < 3:
            return None
        
        # Split mood data into two halves for comparison
        first_half = sum(moods[:len(moods)//2]) / (len(moods)//2)
        second_half = sum(moods[len(moods)//2:]) / (len(moods) - len(moods)//2)
        
        # Calculate mood change between halves
        diff = second_half - first_half
        
        # Detect improving mood trend
        if diff > 0.5:
            return {
                "type": "mood_trend",
                "name": "Improving Mood",
                "trend": "improving",
                "change": f"+{diff:.1f}",
                "confidence": min(abs(diff) / 2, 1.0)
            }
        # Detect declining mood trend
        elif diff < -0.5:
            return {
                "type": "mood_trend",
                "name": "Declining Mood",
                "trend": "declining",
                "change": f"{diff:.1f}",
                "confidence": min(abs(diff) / 2, 1.0)
            }
        # No significant trend detected
        return None
    
    def detect_sleep_mood_correlation(self):
        """Detect correlation between sleep hours and mood ratings"""
        
        # Collect sleep-mood data pairs
        sleep_mood_pairs = []
        
        for e in self.entries:
            if e.sleep_hours and e.mood_rating:
                sleep_mood_pairs.append((e.sleep_hours, e.mood_rating))
        
        # Require minimum 5 data points for correlation
        if len(sleep_mood_pairs) < 5:
            return None
        
        # Separate moods based on sleep duration
        high_sleep = [m for s, m in sleep_mood_pairs if s >= 7]   # Good sleep: 7+ hours
        low_sleep = [m for s, m in sleep_mood_pairs if s < 6]     # Poor sleep: <6 hours
        
        # Check if we have data for both groups
        if not high_sleep or not low_sleep:
            return None
        
        # Calculate average moods for each sleep group
        avg_high = sum(high_sleep) / len(high_sleep)
        avg_low = sum(low_sleep) / len(low_sleep)
        
        # Detect significant correlation (1+ point difference)
        if avg_high > avg_low + 1:
            return {
                "type": "sleep_mood_correlation",
                "name": "Sleep Quality Impact",
                "description": f"Good sleep (7h+) correlates with +{avg_high-avg_low:.1f} higher mood",
                "confidence": 0.8,
                "insight": "Prioritize 7+ hours of sleep"
            }
        return None
    
    def detect_activity_impact(self):
        """Identify which activities correlate with highest mood scores"""
        
        # Dictionary to store mood ratings per activity
        activity_moods = defaultdict(list)
        
        # Collect mood data for each activity
        for e in self.entries:
            if e.activities and e.mood_rating:
                for activity in e.activities:
                    activity_moods[activity].append(e.mood_rating)
        
        # Check if we have activity data
        if not activity_moods:
            return None
        
        # Find activity with highest average mood
        best_activity = None
        best_mood = 0
        
        for activity, moods in activity_moods.items():
            # Require minimum 2 data points per activity
            if len(moods) >= 2:
                avg_mood = sum(moods) / len(moods)
                # Track best performing activity
                if avg_mood > best_mood:
                    best_mood = avg_mood
                    best_activity = activity
        
        # Return pattern if activity has significant positive impact (mood > 6)
        if best_activity and best_mood > 6:
            return {
                "type": "activity_impact",
                "name": f"Positive Activity: {best_activity}",
                "description": f"{best_activity} correlates with avg mood {best_mood:.1f}/10",
                "confidence": 0.75,
                "insight": f"More {best_activity} could improve wellbeing"
            }
        return None
    
    def get_all_patterns(self):
        """Execute all pattern detection methods and return combined results"""
        
        # Initialize patterns list
        patterns = []
        
        # Detect mood trend
        mood_trend = self.detect_mood_trend()
        if mood_trend:
            patterns.append(mood_trend)
        
        # Detect sleep-mood correlation
        sleep_mood = self.detect_sleep_mood_correlation()
        if sleep_mood:
            patterns.append(sleep_mood)
        
        # Detect activity impact
        activity_impact = self.detect_activity_impact()
        if activity_impact:
            patterns.append(activity_impact)
        
        # Return all detected patterns
        return patterns
>>>>>>> Stashed changes
