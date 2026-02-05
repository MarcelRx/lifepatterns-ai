# Database Utilities with Privacy Protection
#-----------------------------------------------------------------
# ALL database functions require user_id to ensure data isolation.
# This prevents cross-user data access and maintains privacy.
# ----------------------------------------------
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any

# Load environment variables from .env file
load_dotenv()

def get_engine():
    """Create and return a database engine connection"""
    # URL encode password to handle special characters
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    
    # Construct PostgreSQL connection URL from environment variables
    url = f"postgresql://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    # Create and return SQLAlchemy engine
    return create_engine(url)

class Entry:
    """Entry data class for storing journal entry information"""
    def __init__(self, row):
        # Unpack database row into object properties
        self.entry_date = row[0]        # Date of the entry
        self.mood_rating = row[1]       # Mood score (1-10)
        self.energy_level = row[2]      # Energy level (1-10)
        self.sleep_hours = row[3]       # Hours of sleep
        self.activities = row[4]        # List of activities performed
        
        # Optional fields (may not be present in all database rows)
        self.sentiment_score = row[5] if len(row) > 5 else 0       # AI sentiment score (-1 to 1)
        self.sentiment_label = row[6] if len(row) > 6 else None    # Sentiment category
        self.keywords = row[7] if len(row) > 7 else []            # Extracted keywords
        self.journal_text = row[8] if len(row) > 8 else ""        # Journal content
        self.emotions = row[9] if len(row) > 9 else {}            # Emotion scores dictionary
        self.topics = row[10] if len(row) > 10 else []            # Detected topics

def get_entries(user_id: int, limit: int = 30) -> List[Entry]:
    """
    Get journal entries for a specific user ONLY - Privacy Protected
    
    Args:
        user_id (int): The unique identifier of the user
        limit (int): Maximum number of entries to retrieve (default: 30)
    
    Returns:
        List[Entry]: List of Entry objects for the specified user
    """
    engine = get_engine()
    
    with engine.connect() as conn:
        # Execute parameterized query with user_id to prevent SQL injection
        result = conn.execute(text("""
            SELECT entry_date, mood_rating, energy_level, sleep_hours, activities,
                   sentiment_score, sentiment_label, keywords, journal_text,
                   emotions, topics
            FROM daily_entries
            WHERE user_id = :user_id
            ORDER BY entry_date DESC
            LIMIT :limit
        """), {"user_id": user_id, "limit": limit})
        
        # Fetch all rows and convert to Entry objects
        rows = result.fetchall()
        return [Entry(row) for row in rows]

def save_entry(data: Dict[str, Any]) -> bool:
    """
    Save a journal entry with strict user isolation
    
    Args:
        data (Dict[str, Any]): Dictionary containing entry data including user_id
    
    Returns:
        bool: True if save successful, False otherwise
    """
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # UPSERT operation: Insert new or update existing entry for same date
            conn.execute(text("""
                INSERT INTO daily_entries 
                (user_id, entry_date, journal_text, mood_rating, energy_level, sleep_hours, activities,
                 sentiment_score, sentiment_label, emotions, keywords, topics)
                VALUES 
                (:user_id, :date, :text, :mood, :energy, :sleep, :activities,
                 :sentiment_score, :sentiment_label, :emotions, :keywords, :topics)
                ON CONFLICT (user_id, entry_date) 
                DO UPDATE SET
                    journal_text = EXCLUDED.journal_text,
                    mood_rating = EXCLUDED.mood_rating,
                    energy_level = EXCLUDED.energy_level,
                    sleep_hours = EXCLUDED.sleep_hours,
                    activities = EXCLUDED.activities,
                    sentiment_score = EXCLUDED.sentiment_score,
                    sentiment_label = EXCLUDED.sentiment_label,
                    emotions = EXCLUDED.emotions,
                    keywords = EXCLUDED.keywords,
                    topics = EXCLUDED.topics,
                    updated_at = CURRENT_TIMESTAMP
            """), data)
            
            # Commit transaction to make changes permanent
            conn.commit()
            return True
            
    except Exception as e:
        # Log error but don't expose details to user
        print(f"Error saving entry: {e}")
        return False

def get_user_stats(user_id: int) -> Dict[str, Any]:
    """
    Get aggregated statistics for a specific user - Privacy Protected
    
    Args:
        user_id (int): The unique identifier of the user
    
    Returns:
        Dict[str, Any]: Dictionary containing user statistics
    """
    engine = get_engine()
    
    with engine.connect() as conn:
        # Execute aggregation query with user isolation
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_entries,
                AVG(mood_rating) as avg_mood,
                AVG(energy_level) as avg_energy,
                AVG(sleep_hours) as avg_sleep
            FROM daily_entries
            WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        # Process results
        row = result.fetchone()
        return {
            "total_entries": row[0] or 0,                     # Total number of entries
            "avg_mood": round(row[1], 1) if row[1] else 0,   # Average mood (rounded)
            "avg_energy": round(row[2], 1) if row[2] else 0, # Average energy (rounded)
            "avg_sleep": round(row[3], 1) if row[3] else 0   # Average sleep (rounded)
        }

def get_all_entries_for_export(user_id: int) -> List[Dict]:
    """
    Get all entries for data export - Privacy Protected
    
    Args:
        user_id (int): The unique identifier of the user
    
    Returns:
        List[Dict]: List of dictionaries containing all user entries for export
    """
    engine = get_engine()
    
    with engine.connect() as conn:
        # Retrieve all entries for the user (no limit for export)
        result = conn.execute(text("""
            SELECT entry_date, mood_rating, energy_level, sleep_hours, activities,
                   sentiment_score, sentiment_label, keywords, journal_text,
                   emotions, topics, created_at
            FROM daily_entries
            WHERE user_id = :user_id
            ORDER BY entry_date DESC
        """), {"user_id": user_id})
        
        # Define column names for dictionary mapping
        columns = ['entry_date', 'mood_rating', 'energy_level', 'sleep_hours', 
                   'activities', 'sentiment_score', 'sentiment_label', 'keywords',
                   'journal_text', 'emotions', 'topics', 'created_at']
        
        # Convert each row to a dictionary with column names as keys
        return [dict(zip(columns, row)) for row in result.fetchall()]