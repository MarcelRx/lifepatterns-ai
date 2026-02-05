# Quick database viewer for LifePatterns AI
# Provides a simple command-line interface to view database contents
# -------------------------------------------------------------------
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build secure database connection string
# URL encode password to handle special characters
password = quote_plus(os.getenv("DB_PASSWORD", ""))

# Construct PostgreSQL connection URL from environment variables
url = f"postgresql://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create SQLAlchemy database engine
engine = create_engine(url)

# Open database connection and execute queries
with engine.connect() as conn:
    # Print header
    print("=" * 50)
    print("LIFEPATTERNS DATABASE")
    print("=" * 50)
    
    # COUNT TOTAL ENTRIES 
    # Execute query to count all entries in daily_entries table
    result = conn.execute(text("SELECT COUNT(*) FROM daily_entries"))
    
    # Fetch the count (returns a tuple, take first element)
    count = result.fetchone()[0]
    
    # Display total entry count
    print(f"\nTotal entries: {count}")
    
    # SHOW RECENT ENTRIES 
    # Execute query to retrieve 5 most recent entries
    result = conn.execute(text("""
        SELECT entry_date, mood_rating, energy_level, LEFT(journal_text, 50)
        FROM daily_entries
        ORDER BY entry_date DESC
        LIMIT 5
    """))
    
    # Display section header
    print("\nRecent entries:")
    print("-" * 50)
    
    # Iterate through query results and display each entry
    for row in result:
        # Format: Date | Mood:X Energy:X | Journal preview...
        print(f"{row[0]} | Mood:{row[1]} Energy:{row[2]} | {row[3]}...")
    
    # Print footer
    print("\n" + "=" * 50)