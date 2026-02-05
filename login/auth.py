# Authentication and user management system
# ------------------------------------------
import os
import secrets
import warnings
from datetime import datetime, timedelta
from typing import Optional, Tuple

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Import security and database libraries
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv
from sqlalchemy import text
from utils.database import get_engine

# Load environment variables from .env file
load_dotenv()

# Configure password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],          # Use bcrypt hashing algorithm
    deprecated="auto",           # Auto-handle deprecated schemes
    bcrypt__rounds=12            # 12 rounds for balance of security/performance
)

# JWT configuration for authentication tokens
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)  # Fallback to random key
ALGORITHM = "HS256"              # HMAC with SHA-256 algorithm
ACCESS_TOKEN_EXPIRE_DAYS = 30    # Token validity duration

# User data class for storing user information
class User:
    def __init__(self, id, username, email, created_at, settings=None):
        self.id = id              # Database user ID
        self.username = username  # Username (unique)
        self.email = email        # Email address (optional)
        self.created_at = created_at  # Account creation timestamp
        self.settings = settings or {}  # User preferences dictionary

class AuthManager:
    """Main authentication manager for user registration, login, and security"""
    
    def __init__(self):
        # Initialize database engine for user data operations
        self.engine = get_engine()
    
    def _prepare_password(self, password):
        """Prepare password for hashing, handling bcrypt's 72-byte limit"""
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            # Truncate to 72 bytes for bcrypt compatibility
            return password_bytes[:72].decode("utf-8", errors="ignore")
        return password
    
    def _hash_password(self, password):
        """Hash password using bcrypt with fallback to passlib"""
        try:
            # Try using native bcrypt library
            import bcrypt
            prepared = self._prepare_password(password)
            password_bytes = prepared.encode("utf-8")
            salt = bcrypt.gensalt(rounds=12)  # Generate secure salt
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode("utf-8")
        except:
            # Fallback to passlib's bcrypt implementation
            prepared = self._prepare_password(password)
            return pwd_context.hash(prepared)
    
    def _verify_password(self, password, hashed):
        """Verify password against stored hash"""
        try:
            # Try using native bcrypt verification
            import bcrypt
            prepared = self._prepare_password(password)
            password_bytes = prepared.encode("utf-8")
            hashed_bytes = hashed.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except:
            # Fallback to passlib verification
            prepared = self._prepare_password(password)
            return pwd_context.verify(prepared, hashed)
    
    def register_user(self, username, password, email=None):
        """Register a new user account with validation"""
        
        # Validate username requirements
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters", None
        
        # Validate password requirements
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters", None
        
        # Check if username already exists
        if self._get_user_by_username(username):
            return False, "Username already exists", None
        
        # Check if email already exists (if provided)
        if email and self._get_user_by_email(email):
            return False, "Email already registered", None
        
        try:
            # Hash password for secure storage
            password_hash = self._hash_password(password)
            
            # Insert new user into database
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""INSERT INTO users (username, email, password_hash, created_at, settings) VALUES (:username, :email, :password_hash, CURRENT_TIMESTAMP, \'{}\') RETURNING id, username, email, created_at, settings"""),
                    {"username": username.lower().strip(), "email": email.lower().strip() if email else None, "password_hash": password_hash}
                )
                
                # Get inserted user data
                row = result.fetchone()
                conn.commit()
                
                # Create User object for session
                user = User(id=row[0], username=row[1], email=row[2], created_at=row[3], settings=row[4])
                return True, "Account created successfully!", user
                
        except Exception as e:
            # Log and return registration error
            print(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}", None
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        
        # Validate input presence
        if not username or not password:
            return False, "Please enter username and password", None
        
        # Retrieve user data with password hash
        user_data = self._get_user_with_password(username)
        
        # Check if user exists
        if not user_data:
            return False, "Invalid username or password", None
        
        # Unpack user data
        user_id, db_username, db_email, password_hash, created_at, settings = user_data
        
        # Verify password against stored hash
        if not self._verify_password(password, password_hash):
            return False, "Invalid username or password", None
        
        # Create User object for successful authentication
        user = User(user_id, db_username, db_email, created_at, settings)
        return True, "Login successful", user
    
    def create_access_token(self, user_id, username):
        """Create JWT access token for authenticated sessions"""
        
        # Calculate token expiration (30 days from now)
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        
        # Prepare JWT payload
        payload = {
            "sub": str(user_id),         # Subject (user ID)
            "username": username,        # Username for identification
            "exp": expire,               # Expiration timestamp
            "iat": datetime.utcnow()     # Issued at timestamp
        }
        
        # Encode and return JWT token
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password with verification"""
        
        # Validate new password requirements
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters"
        
        with self.engine.connect() as conn:
            # Retrieve current password hash
            result = conn.execute(text("SELECT password_hash FROM users WHERE id = :user_id"), {"user_id": user_id})
            row = result.fetchone()
            if not row:
                return False, "User not found"
            
            # Verify current password
            if not self._verify_password(old_password, row[0]):
                return False, "Current password is incorrect"
            
            # Hash and store new password
            new_hash = self._hash_password(new_password)
            conn.execute(text("UPDATE users SET password_hash = :new_hash, updated_at = CURRENT_TIMESTAMP WHERE id = :user_id"), {"new_hash": new_hash, "user_id": user_id})
            conn.commit()
            return True, "Password updated successfully"
    
    def delete_user(self, user_id, password):
        """Delete user account with password verification"""
        
        with self.engine.connect() as conn:
            # Retrieve user's password hash for verification
            result = conn.execute(text("SELECT password_hash FROM users WHERE id = :user_id"), {"user_id": user_id})
            row = result.fetchone()
            if not row:
                return False, "User not found"
            
            # Verify password before deletion
            if not self._verify_password(password, row[0]):
                return False, "Invalid password"
            
            # Delete user from database
            conn.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
            conn.commit()
            return True, "Account deleted"
    
    def _get_user_by_username(self, username):
        """Retrieve user by username (case-insensitive)"""
        
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, email, created_at, settings FROM users WHERE LOWER(username) = LOWER(:username)"), {"username": username})
            row = result.fetchone()
            if row:
                # Return User object if found
                return User(row[0], row[1], row[2], row[3], row[4])
            return None
    
    def _get_user_by_email(self, email):
        """Retrieve user by email (case-insensitive)"""
        
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, email, created_at, settings FROM users WHERE LOWER(email) = LOWER(:email)"), {"email": email})
            row = result.fetchone()
            if row:
                # Return User object if found
                return User(row[0], row[1], row[2], row[3], row[4])
            return None
    
    def _get_user_with_password(self, username):
        """Retrieve user data including password hash for authentication"""
        
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id, username, email, password_hash, created_at, settings FROM users WHERE LOWER(username) = LOWER(:username)"), {"username": username})
            return result.fetchone()