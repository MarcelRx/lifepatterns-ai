# Predict future outcomes based on current patterns
# --------------------------------------------------
import json
from datetime import datetime, timedelta
from statistics import mean, stdev


class ForecastEngine:
    """Forecast future mood and wellbeing based on historical trends and patterns"""
    
    def __init__(self, entries, patterns, groq_client=None):
        # Initialize with user entries, detected patterns, and optional Groq AI client
        self.entries = entries
        self.patterns = patterns
        self.groq_client = groq_client
    
    def generate_forecast(self):
        """Generate complete wellbeing forecast with predictions and interventions"""
        
        # Require minimum 3 entries for forecasting
        if len(self.entries) < 3:
            return None
        
        # Build comprehensive forecast object
        forecast = {
            "current_status": self._assess_current_status(),
            "trajectory": self._predict_trajectory(),
            "risk_assessment": self._assess_risks(),
            "predictions": self._generate_predictions(),
            "interventions": self._suggest_interventions()
        }
        
        # Add AI-powered insights if Groq client is available
        if self.groq_client:
            ai_forecast = self._ai_forecast()
            if ai_forecast:
                forecast["ai_insight"] = ai_forecast
        
        # Return complete forecast
        return forecast
    
    def _assess_current_status(self):
        """Assess current wellbeing status based on recent entries"""
        
        # Extract recent mood and energy ratings (last 3 entries)
        recent_moods = [e.mood_rating for e in self.entries[-3:] if e.mood_rating]
        recent_energy = [e.energy_level for e in self.entries[-3:] if e.energy_level]
        
        # Calculate averages (default to 5 if no data)
        avg_mood = mean(recent_moods) if recent_moods else 5
        avg_energy = mean(recent_energy) if recent_energy else 5
        
        # Determine wellbeing status based on thresholds
        if avg_mood >= 7 and avg_energy >= 6:
            status = "Thriving"
            color = "green"
        elif avg_mood >= 5 and avg_energy >= 4:
            status = "Stable"
            color = "yellow"
        elif avg_mood >= 3:
            status = "Struggling"
            color = "orange"
        else:
            status = "Critical"
            color = "red"
        
        # Return status assessment
        return {
            "status": status,
            "color": color,
            "avg_mood": round(avg_mood, 1),
            "avg_energy": round(avg_energy, 1),
            "assessment": self._status_description(status)
        }
    
    def _status_description(self, status):
        """Return descriptive text for each status level"""
        descriptions = {
            "Thriving": "You're doing great! Maintain your positive habits.",
            "Stable": "You're holding steady. Small improvements can help.",
            "Struggling": "You're having a tough time. Prioritize self-care.",
            "Critical": "Immediate attention needed. Consider professional support."
        }
        return descriptions.get(status, "Monitor your wellbeing closely.")
    
    def _predict_trajectory(self):
        """Predict future trend direction (improving, declining, or stable)"""
        
        # Require minimum 3 entries for trajectory analysis
        if len(self.entries) < 3:
            return {"direction": "stable", "confidence": 0.5}
        
        # Extract all mood ratings
        moods = [e.mood_rating for e in self.entries if e.mood_rating]
        
        if len(moods) < 3:
            return {"direction": "stable", "confidence": 0.5}
        
        # Calculate trend by comparing first vs second half of data
        first_half = mean(moods[:len(moods)//2])
        second_half = mean(moods[len(moods)//2:])
        diff = second_half - first_half
        
        # Determine trajectory based on change magnitude
        if diff > 0.5:
            return {
                "direction": "improving",
                "change": f"+{diff:.1f}",
                "confidence": min(abs(diff) / 2, 0.9),
                "description": "Your wellbeing is trending upward"
            }
        elif diff < -0.5:
            return {
                "direction": "declining",
                "change": f"{diff:.1f}",
                "confidence": min(abs(diff) / 2, 0.9),
                "description": "Your wellbeing is declining without intervention"
            }
        else:
            return {
                "direction": "stable",
                "change": f"{diff:+.1f}",
                "confidence": 0.7,
                "description": "Your wellbeing is stable"
            }
    
    def _assess_risks(self):
        """Assess potential burnout and mental health risks"""
        
        risks = []
        
        # Check for declining trend
        trajectory = self._predict_trajectory()
        if trajectory["direction"] == "declining":
            risks.append({
                "type": "mood_decline",
                "level": "medium" if trajectory["confidence"] < 0.7 else "high",
                "description": "Continued mood decline without intervention",
                "probability": f"{trajectory['confidence']:.0%}"
            })
        
        # Check for low mood streak (multiple days with mood < 4)
        recent_low = [e for e in self.entries[-5:] if e.mood_rating and e.mood_rating < 4]
        if len(recent_low) >= 2:
            risks.append({
                "type": "depression_risk",
                "level": "medium",
                "description": "Multiple low mood days detected",
                "probability": "60%"
            })
        
        # Check for sleep deprivation (multiple days with sleep < 6 hours)
        poor_sleep = [e for e in self.entries[-5:] if e.sleep_hours and e.sleep_hours < 6]
        if len(poor_sleep) >= 3:
            risks.append({
                "type": "burnout_risk",
                "level": "high",
                "description": "Chronic sleep deprivation detected",
                "probability": "75%"
            })
        
        return risks
    
    def _generate_predictions(self):
        """Generate specific mood predictions for next 7 days"""
        
        # Get current trend and mood
        trajectory = self._predict_trajectory()
        current_mood = mean([e.mood_rating for e in self.entries[-3:] if e.mood_rating]) if self.entries else 5
        
        # Extract direction and change magnitude
        direction = trajectory["direction"]
        change = abs(float(trajectory.get("change", "0").replace("+", "")))
        
        # Calculate 7-day prediction based on trend
        if direction == "improving":
            predicted_mood = min(current_mood + change, 10)  # Cap at 10
            outlook = "positive"
        elif direction == "declining":
            predicted_mood = max(current_mood - change, 1)   # Floor at 1
            outlook = "concerning"
        else:
            predicted_mood = current_mood
            outlook = "stable"
        
        # Generate daily predictions for each of next 7 days
        predictions = []
        for day in range(1, 8):
            if direction == "improving":
                daily_mood = min(current_mood + (change * day / 7), 10)
            elif direction == "declining":
                daily_mood = max(current_mood - (change * day / 7), 1)
            else:
                daily_mood = current_mood
            
            predictions.append({
                "day": day,
                "date": (datetime.now() + timedelta(days=day)).strftime("%a"),  # Short day name
                "predicted_mood": round(daily_mood, 1),
                "confidence": max(0.9 - (day * 0.05), 0.5)  # Confidence decreases with time
            })
        
        return {
            "outlook": outlook,
            "current_mood": round(current_mood, 1),
            "predicted_mood_7d": round(predicted_mood, 1),
            "daily_predictions": predictions
        }
    
    def _suggest_interventions(self):
        """Suggest interventions based on current trajectory"""
        
        trajectory = self._predict_trajectory()
        interventions = []
        
        # Different interventions based on trend direction
        if trajectory["direction"] == "declining":
            interventions = [
                {
                    "urgency": "immediate",
                    "action": "Schedule daily 20-minute walk",
                    "impact": "Can reverse decline in 3-5 days",
                    "evidence": "Physical activity boosts mood by 30%"
                },
                {
                    "urgency": "this_week",
                    "action": "Establish consistent sleep schedule",
                    "impact": "Improves emotional regulation",
                    "evidence": "Sleep affects 40% of mood variance"
                },
                {
                    "urgency": "ongoing",
                    "action": "Practice gratitude journaling",
                    "impact": "Long-term resilience building",
                    "evidence": "Shown to improve outlook in 2 weeks"
                }
            ]
        elif trajectory["direction"] == "stable":
            interventions = [
                {
                    "urgency": "this_week",
                    "action": "Add one new positive activity",
                    "impact": "Can shift to improving trajectory",
                    "evidence": "Novel experiences boost dopamine"
                }
            ]
        else:  # improving trajectory
            interventions = [
                {
                    "urgency": "ongoing",
                    "action": "Document what's working",
                    "impact": "Maintain positive momentum",
                    "evidence": "Reinforcement strengthens habits"
                }
            ]
        
        return interventions
    
    def _ai_forecast(self):
        """Use Groq AI for additional personalized insights"""
        
        if not self.groq_client:
            return None
        
        try:
            # Summarize recent entries for AI context
            recent_entries = self.entries[-5:]
            summaries = []
            for e in recent_entries:
                text = e.journal_text[:50] if e.journal_text else "No entry"
                summaries.append(f"Mood {e.mood_rating}: {text}")
            
            summary_text = "\n".join(summaries)
            
            # Create structured prompt for AI
            prompt = f"""Based on these recent entries, give a brief wellness forecast:
            
            {summary_text}
            
            Return ONLY JSON:
            {{
                "key_insight": "one sentence observation",
                "watch_for": "what to monitor",
                "opportunity": "positive action to take"
            }}
            """
            
            # Send request to Groq AI
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a wellness coach. Be empathetic and practical."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            # Parse and return AI response
            return json.loads(response.choices[0].message.content)
            
        # Handle AI errors gracefully
        except Exception as e:
            print(f"AI forecast error: {e}")
            return None