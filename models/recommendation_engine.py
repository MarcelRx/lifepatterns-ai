# Generate personalized recommendations based on patterns
# ---------------------------------------------------------
import json
from datetime import datetime  

class RecommendationEngine:
    """Generate smart recommendations from detected behavioral patterns"""
    
    def __init__(self, patterns, entries, groq_client=None):
        # Initialize with detected patterns, user entries, and optional AI client
        self.patterns = patterns
        self.entries = entries
        self.groq_client = groq_client
    
    def generate_recommendations(self):
        """Generate all recommendations from rule-based and AI-powered methods"""
        
        # Initialize recommendations list
        recommendations = []
        
        # Generate mood-based recommendation
        mood_rec = self._mood_recommendation()
        if mood_rec:
            recommendations.append(mood_rec)
        
        # Generate sleep-based recommendation
        sleep_rec = self._sleep_recommendation()
        if sleep_rec:
            recommendations.append(sleep_rec)
        
        # Generate activity-based recommendation
        activity_rec = self._activity_recommendation()
        if activity_rec:
            recommendations.append(activity_rec)
        
        # Generate AI-powered recommendation (if Groq client available and enough data)
        if self.groq_client and len(self.entries) >= 3:
            ai_rec = self._ai_recommendation()
            if ai_rec:
                recommendations.append(ai_rec)
        
        # Return all generated recommendations
        return recommendations
    
    def _mood_recommendation(self):
        """Generate recommendation based on detected mood trends"""
        
        # Find mood trend pattern from detected patterns
        mood_pattern = None
        for p in self.patterns:
            if p.get("type") == "mood_trend":
                mood_pattern = p
                break
        
        # Return None if no mood pattern detected
        if not mood_pattern:
            return None
        
        # Get trend direction (improving or declining)
        trend = mood_pattern.get("trend")
        
        # Generate recommendation for declining mood
        if trend == "declining":
            return {
                "id": "mood_declining",
                "category": "mental_health",
                "title": "Reverse Negative Trend",
                "description": f"Your mood has declined by {mood_pattern.get('change', '')} recently.",
                "action": "Try 10-minute morning meditation or a 20-minute walk daily",
                "expected_impact": "Mood improvement in 3-5 days",
                "confidence": mood_pattern.get("confidence", 0.7),
                "priority": "high"
            }
        
        # Generate recommendation for improving mood
        elif trend == "improving":
            return {
                "id": "mood_improving",
                "category": "wellness",
                "title": "Maintain Positive Momentum",
                "description": "Your mood is improving! Keep doing what works.",
                "action": "Journal what's going well to reinforce positive patterns",
                "expected_impact": "Continued wellbeing",
                "confidence": mood_pattern.get("confidence", 0.7),
                "priority": "medium"
            }
        
        # Return None for stable mood (no significant trend)
        return None
    
    def _sleep_recommendation(self):
        """Generate recommendation based on sleep patterns and correlations"""
        
        # Find sleep-mood correlation pattern
        sleep_pattern = None
        for p in self.patterns:
            if p.get("type") == "sleep_mood_correlation":
                sleep_pattern = p
                break
        
        # Generate recommendation if sleep-mood correlation detected
        if sleep_pattern:
            return {
                "id": "sleep_priority",
                "category": "sleep",
                "title": "Prioritize Sleep Quality",
                "description": sleep_pattern.get("description", ""),
                "action": "Aim for 7-8 hours sleep. Avoid screens 1 hour before bed.",
                "expected_impact": "+1.5 mood improvement",
                "confidence": sleep_pattern.get("confidence", 0.8),
                "priority": "high"
            }
        
        # Check for chronic sleep deficit (multiple days with <6 hours)
        low_sleep_days = [e for e in self.entries if e.sleep_hours and e.sleep_hours < 6]
        if len(low_sleep_days) >= 2:
            return {
                "id": "sleep_deficit",
                "category": "sleep",
                "title": "Catch Up on Sleep",
                "description": f"You had {len(low_sleep_days)} days with less than 6 hours sleep recently.",
                "action": "Go to bed 30 minutes earlier tonight. Create a bedtime routine.",
                "expected_impact": "Better energy and focus tomorrow",
                "confidence": 0.75,
                "priority": "high"
            }
        
        # Return None if no sleep issues detected
        return None
    
    def _activity_recommendation(self):
        """Generate recommendation based on positive activity impact"""
        
        # Find activity impact pattern
        activity_pattern = None
        for p in self.patterns:
            if p.get("type") == "activity_impact":
                activity_pattern = p
                break
        
        # Generate recommendation if positive activity detected
        if activity_pattern:
            # Extract activity name from pattern title
            activity = activity_pattern.get("name", "").replace("Positive Activity: ", "")
            return {
                "id": f"activity_{activity.lower()}",
                "category": "lifestyle",
                "title": f"Do More {activity}",
                "description": activity_pattern.get("description", ""),
                "action": f"Schedule {activity} at least 3 times this week",
                "expected_impact": "Improved mood and energy",
                "confidence": activity_pattern.get("confidence", 0.7),
                "priority": "medium"
            }
        
        # Return None if no positive activity pattern detected
        return None
    
    def _ai_recommendation(self):
        """Use Groq AI to generate personalized, context-aware recommendation"""
        
        # Check if Groq client is available
        if not self.groq_client:
            return None
        
        try:
            # Calculate recent averages for AI context
            recent_moods = [e.mood_rating for e in self.entries[-5:] if e.mood_rating]
            avg_mood = sum(recent_moods) / len(recent_moods) if recent_moods else 5
            
            recent_sleep = [e.sleep_hours for e in self.entries[-5:] if e.sleep_hours]
            avg_sleep = sum(recent_sleep) / len(recent_sleep) if recent_sleep else 7
            
            # Create structured prompt for AI
            prompt = f"""Based on this user's recent data, give ONE specific recommendation:
            
            Recent average mood: {avg_mood:.1f}/10
            Recent average sleep: {avg_sleep:.1f} hours
            Detected patterns: {[p.get('name') for p in self.patterns]}
            
            Return ONLY JSON:
            {{
                "title": "short title",
                "action": "specific actionable step",
                "rationale": "why this helps",
                "expected_impact": "what will improve"
            }}
            """
            
            # Send request to Groq AI
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a wellness coach. Give practical advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse AI response
            result = json.loads(response.choices[0].message.content)
            
            # Format AI recommendation for consistency
            return {
                "id": "ai_generated",
                "category": "ai_insight",
                "title": result.get("title", "Personalized Tip"),
                "description": result.get("rationale", ""),
                "action": result.get("action", ""),
                "expected_impact": result.get("expected_impact", "Improvement in wellbeing"),
                "confidence": 0.8,
                "priority": "high",
                "source": "AI"
            }
            
        # Handle AI errors gracefully
        except Exception as e:
            print(f"AI recommendation error: {e}")
            return None