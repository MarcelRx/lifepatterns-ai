import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

def test_connection():
    """Test PostgreSQL database connection"""
    
    # Retrieve database configuration from environment variables
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "lifepatterns_db")
    user = os.getenv("DB_USER", "mohsenrassam")
    password = os.getenv("DB_PASSWORD", "")
    
    # URL encode password to handle special characters
    password_encoded = quote_plus(password)
    
    # Construct PostgreSQL connection URL
    url = f"postgresql://{user}:{password_encoded}@{host}:{port}/{dbname}"
    
    # Display connection information (for debugging)
    print(f"Connecting to: {host}:{port}/{dbname} as {user}")
    
    # Attempt database connection
    try:
        # Create SQLAlchemy engine
        engine = create_engine(url)
        
        # Test connection with version query
        with engine.connect() as conn:
            # Query PostgreSQL version
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"Connected!")
            print(f"PostgreSQL version: {version[:50]}...")
            
            # List all tables in public schema
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public';
            """))
            tables = [row[0] for row in result]
            print(f"Tables found: {tables}")
            
            # Count records in users table
            result = conn.execute(text("SELECT COUNT(*) FROM users;"))
            count = result.fetchone()[0]
            print(f"Users in database: {count}")
            
            return True
            
    # Handle connection errors
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# Run connection test when script is executed directly
if __name__ == "__main__":
    test_connection()