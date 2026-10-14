# Configuration validation and management
# ----------------------------------------
import os
import sys

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigError(Exception):
    """Raised when configuration is invalid or missing"""

    pass


def get_required_env(var_name: str, default: str = None) -> str:
    """
    Get a required environment variable.

    Args:
        var_name: Name of the environment variable
        default: Optional default value (only for development)

    Returns:
        The environment variable value

    Raises:
        ConfigError: If the variable is missing in production
    """
    value = os.getenv(var_name, default)

    if not value:
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            raise ConfigError(
                f"Required environment variable '{var_name}' is not set. "
                f"This is required in production."
            )
        else:
            # In development, allow some variables to be missing with warning
            print(f"WARNING: {var_name} not set - using default or placeholder")

    return value


def validate_secret_key(secret_key: str) -> bool:
    """
    Validate that SECRET_KEY is not a placeholder or insecure.

    Args:
        secret_key: The SECRET_KEY value to validate

    Returns:
        True if valid, False otherwise
    """
    environment = os.getenv("ENVIRONMENT", "development")

    # Known insecure placeholders
    insecure_placeholders = [
        "your-secret-key-here",
        "your-secret-key-here-change-in-production",
        "change-this-in-production",
        "secret-key-placeholder",
        "test-secret-key",
        "dev-secret-key",
    ]

    # Check for insecure placeholders
    if secret_key.lower() in [p.lower() for p in insecure_placeholders]:
        if environment == "production":
            raise ConfigError(
                "SECRET_KEY is using a placeholder value. "
                'Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        else:
            print(
                "WARNING: SECRET_KEY is using a placeholder value. "
                "This is OK for development but must be changed in production."
            )
            return False

    # Check minimum length (at least 32 characters for hex, 43 for urlsafe)
    if len(secret_key) < 32:
        if environment == "production":
            raise ConfigError(
                f"SECRET_KEY is too short ({len(secret_key)} chars). "
                'Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        else:
            print(
                f"WARNING: SECRET_KEY is short ({len(secret_key)} chars). Recommended: 32+ chars."
            )

    return True


def get_secret_key() -> str:
    """
    Get and validate SECRET_KEY for JWT signing.

    Returns:
        The validated SECRET_KEY

    Raises:
        ConfigError: If SECRET_KEY is invalid or missing in production
    """
    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            raise ConfigError(
                "SECRET_KEY is not set. This is required for JWT token signing. "
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        else:
            # In development, generate a temporary key but warn
            import secrets

            secret_key = secrets.token_hex(32)
            print(
                f"WARNING: SECRET_KEY not set. Generated temporary key for development: {secret_key[:8]}..."
            )
            print("Set SECRET_KEY in .env for persistence.")

    validate_secret_key(secret_key)
    return secret_key


def validate_database_config() -> dict:
    """
    Validate database configuration and return connection parameters.

    Returns:
        Dictionary with database connection parameters

    Raises:
        ConfigError: If required database parameters are missing
    """
    environment = os.getenv("ENVIRONMENT", "development")

    # Check for DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # If DATABASE_URL is set, use it
        return {"url": database_url}

    # Otherwise, check individual parameters
    required_params = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_params = [p for p in required_params if not os.getenv(p)]

    if missing_params:
        if environment == "production":
            raise ConfigError(
                f"Missing required database parameters: {', '.join(missing_params)}. "
                f"Set DATABASE_URL or individual DB_* environment variables."
            )
        else:
            print(f"WARNING: Missing database parameters: {', '.join(missing_params)}")
            print("Database operations may fail.")

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "name": os.getenv("DB_NAME", "lifepatterns_db"),
        "user": os.getenv("DB_USER", "lifepatterns_user"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def is_external_ai_enabled() -> bool:
    """
    Determine if external AI processing is enabled based on configuration.

    Secure-by-default: Returns False unless explicitly set to "true".

    Behavior:
    - Variable absent: external AI disabled (False)
    - Value "false": external AI disabled (False)
    - Value "true": external AI eligible (True, subject to API key availability)
    - Values with surrounding whitespace: trimmed before evaluation
    - Case variations: case-insensitive (True, TRUE, true all valid)
    - Invalid values (yes, 1, enabled, arbitrary strings): fail closed (False)

    Returns:
        bool: True if external AI is explicitly enabled, False otherwise
    """
    value = os.getenv("ENABLE_EXTERNAL_AI", "false")
    if value is None:
        return False

    # Trim whitespace
    value = value.strip()

    # Case-insensitive check for "true"
    return value.lower() == "true"


def validate_all_config() -> None:
    """
    Validate all critical configuration at application startup.

    Raises:
        ConfigError: If critical configuration is invalid
    """
    environment = os.getenv("ENVIRONMENT", "development")

    print(f"Validating configuration for environment: {environment}")

    try:
        # Validate SECRET_KEY
        get_secret_key()

        # Validate database config
        validate_database_config()

        # Optional: Validate Groq API key if provided
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and groq_key.startswith("gsk_your_"):
            print(
                "WARNING: GROQ_API_KEY appears to be a placeholder. AI features may not work."
            )

        print("Configuration validation complete.")

    except ConfigError as e:
        print(f"Configuration error: {e}")
        if environment == "production":
            sys.exit(1)
        else:
            print("Continuing in development mode with warnings.")
