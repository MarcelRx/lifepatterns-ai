# Environment Setup Guide

## Quick Start

1. **Copy the appropriate example file:**

   ```bash
   # For local development
   cp .env.example .env

   # For production deployment
   cp .env.production.example .env
   ```

2. **Edit .env with your values:**
   - Set `DATABASE_URL` or individual `DB_*` variables
   - Generate `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
   - (Optional) Add `GROQ_API_KEY` for AI features

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Configuration Files

The repository provides three environment configuration templates:

- **`.env.example`** - Local development template
- **`.env.production.example`** - Production deployment template
- **`.env.test`** - CI/CD testing configuration (no secrets required)

## Required Variables

All environments require:

- `SECRET_KEY` - JWT token signing key
- Database connection (either `DATABASE_URL` or `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)

## Optional Variables

- `GROQ_API_KEY` - Groq API key for AI features (uses local fallback if not set)
- `OPENWEATHER_API_KEY` - OpenWeatherMap API key (feature not yet implemented)

## Note on Encryption Variables

The following variables are documented in .env files but are not currently implemented:

- `ENCRYPT_DATA` - Not implemented in application code
- `ENCRYPTION_KEY` - Not implemented in application code
- Journal entries are stored in plaintext in PostgreSQL

## Generating Keys

**SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Validation

The application validates configuration at startup:

- Development mode: Shows warnings for missing/invalid configuration
- Production mode: Fails with clear error messages
- Rejects known insecure placeholders

For more details, see:

- `.github/SECRETS_MAPPING.md` - GitHub Actions and deployment secrets
- `SECURITY.md` - Security practices and credential rotation
- `README.md` - Complete deployment documentation
