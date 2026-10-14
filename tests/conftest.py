# Pytest configuration
import os

from dotenv import load_dotenv

# Load test environment variables from .env.test if it exists
# Otherwise use default test values
try:
    load_dotenv(".env.test")
except:
    pass

# Set test environment
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
