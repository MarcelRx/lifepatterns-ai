# Deployment Documentation

## Purpose and Scope

This document describes the deployment process for LifePatterns AI, including prerequisites, installation steps, configuration, local execution, production deployment, CI/CD workflows, and troubleshooting.

**Scope:**

- Verified supported deployment targets
- Prerequisites and runtime versions
- Installation and build steps
- Configuration and required environment variables
- Local execution commands
- Test and production build commands
- Database or migration steps
- CI/CD workflow and repository configuration
- Runtime secrets vs CI-only secrets
- Health checks and observability (where implemented)
- Rollback or recovery procedures (where supported)
- Common failures and troubleshooting
- Known deployment limitations
- Deployment verification status

## Verified Supported Deployment Target

**Primary Target**: Self-hosted deployment

**Supported Platforms**:

- Local development (macOS, Linux, Windows)
- Streamlit Cloud (documentation provided, not verified)
- Docker container (documentation provided, not verified)
- Generic cloud hosting with Python support (documentation provided, not verified)

**Deployment Verification Status**:

- Local development: **Verified** (tested on macOS with Python 3.12.8)
- Streamlit Cloud: **Not verified** (instructions provided but not executed)
- Docker: **Not verified** (Dockerfile example provided but not built)
- Production cloud hosting: **Not verified** (no production deployment executed)

## Prerequisites and Runtime Versions

### System Requirements

**Operating System**:

- macOS 10.15+ (Catalina or later)
- Linux (Ubuntu 20.04+, Debian 10+, or equivalent)
- Windows 10+ (with WSL2 recommended for development)

**Hardware**:

- RAM: 1GB minimum, 2GB recommended
- CPU: Any modern processor
- Disk: 500MB for application + dependencies

### Software Requirements

**Python**: 3.9 or higher

**Tested Versions**:

- Python 3.9 (CI/CD configuration)
- Python 3.12.8 (local verification)

**Python Package Manager**: pip (included with Python)

**Database**: PostgreSQL 15 or higher

**Optional Software**:

- Git (for cloning repository)
- Docker (for containerized deployment, optional)
- Virtual environment tool (venv or conda)

### External Services

**Required**:

- PostgreSQL database (local or remote)

**Optional**:

- Groq API key (for AI features)
- OpenWeatherMap API key (feature not implemented)

## Installation and Build Steps

### Local Development Installation

**Step 1: Clone Repository**

```bash
git clone https://github.com/MarcelRx/lifepatterns-ai.git
cd lifepatterns-ai
```

**Step 2: Create Virtual Environment**

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda (alternative)
conda create -n lifepatterns python=3.9
conda activate lifepatterns
```

**Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Dependencies Installed**:

- Streamlit 1.28.0
- SQLAlchemy 2.0.23
- psycopg2-binary 2.9.9
- groq 0.4.2
- pandas 2.1.3
- numpy 1.26.2
- textblob 0.17.1
- plotly 5.18.0
- python-jose 3.3.0
- passlib 1.7.4
- pytest 7.4.3
- flake8 6.1.0
- black 23.11.0
- And more (see requirements.txt)

**Step 4: Setup PostgreSQL Database**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE lifepatterns_db;
CREATE USER lifepatterns_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE lifepatterns_db TO lifepatterns_user;
\q
```

**Step 5: Run Database Setup Script**

```bash
psql -U postgres -d lifepatterns_db -f utils/setup_postgres.sql
```

**Setup Script Creates**:

- Tables: users, daily_entries, detected_patterns, recommendations
- Indexes for performance
- Triggers for updated_at timestamps
- Views for common queries
- Sample test data

**Step 6: Configure Environment**

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# - DATABASE_URL or individual DB_* variables
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_hex(32))")
# Optional:
# - GROQ_API_KEY (for AI features)
# - ENABLE_EXTERNAL_AI=false (default, set to true to enable external AI processing)
```

**Step 7: Run Application**

```bash
streamlit run app.py
```

**Access**: http://localhost:8501

### Docker Installation (Not Verified)

**Step 1: Create Dockerfile**

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Step 2: Build Image**

```bash
docker build -t lifepatterns-ai .
```

**Step 3: Run Container**

```bash
docker run -p 8501:8501 \
  -e SECRET_KEY=your-production-secret-key \
  -e DATABASE_URL=postgresql://user:pass@host:port/db \
  -e ENVIRONMENT=production \
  lifepatterns-ai
```

**Note**: Docker deployment not verified in this session

## Configuration and Required Environment Variables

### Required Environment Variables

**SECRET_KEY** (Required):

- Purpose: JWT token signing
- Generation: `python -c "import secrets; print(secrets.token_hex(32))"`
- Minimum length: 32 characters
- Must not be placeholder value (e.g., "your-secret-key-here")

**Database Connection** (Required, choose one):

**Option 1: DATABASE_URL**

```
DATABASE_URL=postgresql://user:password@host:port/database
```

**Option 2: Individual DB\_\* Variables**

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lifepatterns_db
DB_USER=lifepatterns_user
DB_PASSWORD=your_secure_password
```

### Optional Environment Variables

**ENABLE_EXTERNAL_AI** (Optional):

- Purpose: Enable or disable external AI processing (Groq API)
- Default: "false" (secure-by-default)
- Set to "true" to enable external AI processing (requires operator configuration AND explicit user consent)
- When disabled or consent not granted: uses local TextBlob/keyword-based analysis only (no data sent externally)

**GROQ_API_KEY** (Optional):

- Purpose: Groq API key for AI features
- Source: https://console.groq.com/keys
- Required only if `ENABLE_EXTERNAL_AI=true`
- Fallback: Local TextBlob analysis if not set or API fails

**OPENWEATHER_API_KEY** (Optional):

- Purpose: OpenWeatherMap API key for weather correlation
- Status: Feature not implemented

**ENVIRONMENT** (Optional):

- Values: `development`, `production`, `test`
- Default: `development`
- Impact: Configuration validation behavior (warnings vs errors)

**DEBUG** (Optional):

- Values: `True`, `False`
- Default: `True`
- Status: Documented but not used in application code

**DB_SSL_MODE** (Optional):

- Values: `disable`, `allow`, `prefer`, `require`, `verify-ca`, `verify-full`
- Default: `prefer`
- Status: Documented but not enforced by application code

**ENCRYPT_DATA** (Optional):

- Values: `True`, `False`
- Default: `False`
- Status: Documented but not implemented in application code

**ENCRYPTION_KEY** (Optional):

- Purpose: Data encryption key
- Status: Documented but not implemented in application code

### Configuration Files

**Development**: `.env.example`
**Production**: `.env.production.example`
**Testing**: `.env.test`

### Configuration Validation

**Implementation**: `utils/config.py`

**Validation Rules**:

- Development mode: Warnings for missing/invalid configuration
- Production mode: Errors for missing/invalid configuration
- Rejects known insecure placeholders
- Validates SECRET_KEY length and format

**Validation Execution**: Automatic at application startup (`app.py` lines 12-23)

## Local Execution Commands

### Run Application

```bash
streamlit run app.py
```

**Default Behavior**:

- Port: 8501
- Address: localhost
- Auto-reload: Enabled

### Custom Port

```bash
streamlit run app.py --server.port 8502
```

### Network Access

```bash
streamlit run app.py --server.address 0.0.0.0
```

**Warning**: Exposes application to network, use with caution

### Run with Configuration File

```bash
# .env file is automatically loaded by python-dotenv
# No additional command needed
streamlit run app.py
```

## Test and Production Build Commands

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_nlp_processor.py -v
```

### Linting

```bash
# Critical errors only
flake8 . --select=E9,F63,F7,F82 --show-source

# Style and complexity
flake8 . --max-complexity=10 --max-line-length=127
```

### Formatting

```bash
# Check formatting
black . --check

# Apply formatting
black .
```

### Type Checking

**Status**: Not configured (mypy not in requirements.txt)

## Database or Migration Steps

### Initial Database Setup

**Script**: `utils/setup_postgres.sql`

**Execution**:

```bash
psql -U postgres -d lifepatterns_db -f utils/setup_postgres.sql
```

**Setup Script Actions**:

1. Creates tables (users, daily_entries, detected_patterns, recommendations)
2. Creates indexes for performance
3. Creates triggers for updated_at timestamps
4. Creates views for common queries
5. Inserts sample test data

### Database Migration Strategy

**Current Status**: No migration framework configured

**Alembic**: Installed (1.12.1) but not configured

**Migration Process**: Manual SQL script execution

**Recommendation**: Configure Alembic for automated schema versioning

### Schema Changes

**Current Schema**: Single version (initial schema)

**No Schema Evolution**: No changes since initial creation

**Future Schema Changes**: Would require manual SQL execution or Alembic configuration

## CI/CD Workflow and Repository Configuration

### GitHub Actions Workflow

**Location**: `.github/workflows/ci.yml`

**Triggers**:

- Push to main or develop branches
- Pull requests to main branch

### Workflow Jobs

**Job 1: Linting**

**Runs-on**: ubuntu-24.04

**Steps**:

1. Checkout code
2. Set up Python 3.9
3. Install dependencies
4. Run flake8 (critical errors)
5. Run flake8 (style and complexity, non-blocking)

**Job 2: Test**

**Runs-on**: ubuntu-latest

**Services**:

- PostgreSQL 15 (service container)

**Steps**:

1. Checkout code
2. Set up Python 3.9
3. Install dependencies
4. Run pytest with test database configuration
5. Run Gitleaks secret scanning

**Environment Variables** (Job 2):

```
ENVIRONMENT=test
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=test_password
SECRET_KEY=test-secret-key-for-ci-only
```

### CI/CD Secrets Configuration

**Documentation**: `.github/SECRETS_MAPPING.md`

**Production Secrets** (to be configured in GitHub):

- SECRET_KEY
- DATABASE*URL or DB*\* variables
- GROQ_API_KEY (optional)
- OPENWEATHER_API_KEY (optional)

**CI Secrets** (hardcoded in workflow):

- Test database credentials (not production secrets)

**Secret Rotation**: Manual process documented in SECRETS_MAPPING.md

## Runtime Secrets vs CI-Only Secrets

### Runtime Secrets

**Used by Application**:

- SECRET_KEY (JWT signing)
- DATABASE*URL or DB*\* variables (database connection)
- GROQ_API_KEY (AI features)
- OPENWEATHER_API_KEY (not implemented)

**Storage**:

- Development: `.env` file (not committed)
- Production: Environment variables or secret management service
- Streamlit Cloud: Secrets dashboard
- Docker: Environment variables passed at runtime

### CI-Only Secrets

**Used by CI/CD Only**:

- Test database credentials (test_user, test_password)
- Test SECRET_KEY (test-secret-key-for-ci-only)

**Storage**:

- Hardcoded in `.github/workflows/ci.yml`
- Not used by production application

**Security**: Test-only credentials, safe to commit

## Health Checks and Observability

### Health Checks

**Status**: **Not implemented**

**No Health Check Endpoints**:

- No `/health` endpoint
- No `/ready` endpoint
- No database connection health check

**Database Connection Test**:

- Location: `data/database.py`, function `test_connection()`
- Purpose: Manual connection testing utility
- Execution: Manual (`python data/database.py`)
- Not integrated into application

### Observability

**Status**: **Not implemented**

**No Monitoring**:

- No application performance monitoring (APM)
- No error tracking (e.g., Sentry)
- No logging framework (only print statements)
- No metrics collection

**No Alerts**:

- No alerting for errors
- No alerting for performance issues
- No alerting for security events

**Recommendations**:

- Implement health check endpoint
- Add structured logging framework
- Integrate error tracking (Sentry)
- Add monitoring and alerting

## Rollback or Recovery Procedures

### Rollback Procedures

**Status**: **Not implemented**

**No Automated Rollback**:

- No deployment versioning
- No blue/green deployment
- No canary deployment
- No automatic rollback on failure

**Manual Rollback**:

- Git-based: `git checkout <previous-commit>`
- Database: Manual restore from backup (if backup exists)

### Recovery Procedures

**Database Recovery**:
**Status**: **Not implemented**

**No Automated Backups**:

- Backup configuration documented but not implemented
- No automated backup scheduling
- No backup retention policy

**Manual Backup**:

```bash
pg_dump -U lifepatterns_user lifepatterns_db > backup.sql
```

**Manual Restore**:

```bash
psql -U lifepatterns_user lifepatterns_db < backup.sql
```

**Recommendations**:

- Implement automated database backups
- Implement backup retention policy
- Document and test recovery procedures
- Consider point-in-time recovery

## Common Failures and Troubleshooting

### Database Connection Failures

**Symptom**: "Connection failed" error

**Causes**:

1. PostgreSQL not running
2. Incorrect database credentials
3. Database not created
4. Network connectivity issues

**Troubleshooting**:

```bash
# Test PostgreSQL connection
psql -U postgres -d lifepatterns_db

# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list postgresql     # macOS

# Verify database exists
psql -U postgres -l
```

**Solution**:

- Start PostgreSQL service
- Verify credentials in `.env`
- Create database if missing
- Check network connectivity

### Configuration Validation Failures

**Symptom**: "Configuration error" at startup

**Causes**:

1. SECRET_KEY missing or too short
2. Database credentials missing
3. Placeholder values in production

**Troubleshooting**:

```bash
# Check environment variables
echo $SECRET_KEY
echo $DATABASE_URL

# Validate configuration
python -c "from utils.config import validate_all_config; validate_all_config()"
```

**Solution**:

- Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- Set DATABASE*URL or DB*\* variables
- Replace placeholder values in production

### Import Errors

**Symptom**: Module import errors

**Causes**:

1. Dependencies not installed
2. Virtual environment not activated
3. Python version mismatch

**Troubleshooting**:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Reinstall dependencies
pip install -r requirements.txt
```

**Solution**:

- Activate virtual environment
- Install dependencies
- Ensure Python 3.9+

### Groq API Failures

**Symptom**: AI features not working

**Causes**:

1. GROQ_API_KEY missing or invalid
2. Groq API service down
3. Rate limit exceeded

**Troubleshooting**:

```bash
# Test Groq connection
python models/groq_client.py

# Check API key
echo $GROQ_API_KEY
```

**Solution**:

- Verify GROQ_API_KEY in `.env`
- Application will fall back to local TextBlob
- Check Groq service status

### Port Already in Use

**Symptom**: "Address already in use" error

**Causes**:

1. Another process using port 8501
2. Previous Streamlit instance still running

**Troubleshooting**:

```bash
# Find process using port 8501
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill process
kill <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Solution**:

- Kill existing process
- Use different port: `streamlit run app.py --server.port 8502`

## Known Deployment Limitations

### Scalability Limitations

1. **Single-Process Execution**: Streamlit runs as single process, no horizontal scaling
2. **No Connection Pooling**: Each query creates new database connection
3. **No Caching**: Redis configured but not used
4. **No Load Balancing**: Not designed for high availability

### Security Limitations

1. **No SSL Enforcement**: DB_SSL_MODE documented but not enforced
2. **No Encryption at Rest**: Journal text stored in plaintext
3. **No Rate Limiting**: Authentication endpoints not rate-limited
4. **No Monitoring**: No security event monitoring

### Operational Limitations

1. **No Health Checks**: No health check endpoints
2. **No Observability**: No monitoring or logging framework
3. **No Automated Backups**: Backup documented but not implemented
4. **No Rollback Mechanism**: No automated rollback on deployment failure

### Feature Limitations

1. **No Real-Time Updates**: Manual page refresh required
2. **No Multi-Language Support**: English only
3. **No Mobile Optimization**: Not responsive for mobile devices
4. **No Background Jobs**: All processing synchronous

## Deployment Verification Status

### Local Development

**Status**: **Verified**

**Verification Date**: 2026-10-14

**Verification Steps**:

1. Cloned repository
2. Created virtual environment
3. Installed dependencies
4. Ran unit tests: 15/15 passing
5. Started application with `streamlit run app.py`
6. Verified application accessible at http://localhost:8501

**Result**: Local development deployment successful

### Streamlit Cloud

**Status**: **Not verified**

**Evidence**: Instructions provided in README but not executed

**Verification Required**:

- Push code to GitHub
- Connect Streamlit Cloud to repository
- Configure secrets in Streamlit Cloud dashboard
- Deploy and verify functionality

### Docker Deployment

**Status**: **Not verified**

**Evidence**: Dockerfile example provided but not built

**Verification Required**:

- Build Docker image
- Run container with environment variables
- Verify application functionality
- Test database connectivity

### Production Cloud Hosting

**Status**: **Not verified**

**Evidence**: Generic instructions provided but not executed

**Verification Required**:

- Deploy to cloud platform (AWS, GCP, Azure, etc.)
- Configure environment variables
- Set up PostgreSQL database
- Verify end-to-end functionality

### CI/CD Pipeline

**Status**: **Not executed**

**Evidence**: GitHub Actions workflow configured but not triggered

**Verification Required**:

- Push code to trigger workflow
- Verify linting job passes
- Verify test job passes
- Verify secret scanning passes

## Deployment Checklist

### Pre-Deployment Checklist

- [ ] Generate unique SECRET_KEY (not used in development)
- [ ] Set ENVIRONMENT=production
- [ ] Configure production database credentials
- [ ] Set up PostgreSQL database (if not using existing)
- [ ] Run database setup script (`utils/setup_postgres.sql`)
- [ ] Configure GROQ_API_KEY (if using AI features)
- [ ] Review and rotate any exposed credentials
- [ ] Test configuration validation in production mode
- [ ] Verify no hardcoded secrets in code
- [ ] Run tests and ensure all pass
- [ ] Run linting and fix critical errors

### Production Deployment Checklist

- [ ] Deploy application to production environment
- [ ] Configure environment variables in production
- [ ] Verify database connectivity
- [ ] Verify application accessible
- [ ] Test user registration
- [ ] Test login functionality
- [ ] Test daily entry submission
- [ ] Test pattern discovery
- [ ] Test data export
- [ ] Monitor error logs
- [ ] Verify no configuration warnings in production mode

### Post-Deployment Checklist

- [ ] Set up monitoring (if available)
- [ ] Configure backup strategy
- [ ] Document deployment details
- [ ] Review access controls
- [ ] Test rollback procedure
- [ ] Update documentation with deployment details
- [ ] Notify stakeholders of deployment

## Recommendations

### Immediate Improvements

1. **Implement Health Checks**:
   - Add `/health` endpoint
   - Add database connection health check
   - Integrate with monitoring system

2. **Implement Structured Logging**:
   - Replace print statements with logging module
   - Add log levels (DEBUG, INFO, WARNING, ERROR)
   - Configure log rotation

3. **Implement Database Backups**:
   - Set up automated PostgreSQL backups
   - Configure backup retention policy
   - Test backup and recovery procedures

4. **Implement Error Tracking**:
   - Integrate error tracking service (e.g., Sentry)
   - Configure error alerts
   - Monitor error rates

### Medium-Term Improvements

5. **Configure Alembic for Migrations**:
   - Initialize Alembic
   - Create initial migration
   - Document migration process

6. **Implement Database SSL**:
   - Enforce SSL in production
   - Use DB_SSL_MODE environment variable
   - Test SSL connection

7. **Implement Rate Limiting**:
   - Add rate limiting to authentication endpoints
   - Track failed login attempts
   - Implement account lockout

8. **Implement Monitoring**:
   - Add application performance monitoring
   - Add security event monitoring
   - Set up alerts for anomalies

### Long-Term Improvements

9. **Implement High Availability**:
   - Add load balancing
   - Implement database replication
   - Configure failover mechanisms

10. **Implement Blue/Green Deployment**:
    - Set up blue/green deployment strategy
    - Implement automated rollback
    - Configure canary deployments

## Conclusion

LifePatterns AI provides clear deployment instructions for local development and outlines production deployment strategies. Local development has been verified successfully. However, production deployment (Streamlit Cloud, Docker, cloud hosting) has not been verified.

**Strengths**:

- Clear local development setup instructions
- Comprehensive environment variable documentation
- CI/CD workflow configured with linting, tests, and secret scanning
- Database setup script provided
- Configuration validation at startup

**Limitations**:

- No health check endpoints
- No observability or monitoring
- No automated backups
- No rollback mechanisms
- Production deployment not verified
- No database SSL enforcement
- No migration framework configured

**Priority Actions**:

1. Implement health check endpoints
2. Add structured logging framework
3. Implement automated database backups
4. Integrate error tracking
5. Configure Alembic for migrations
6. Enforce database SSL in production
7. Verify production deployment (Streamlit Cloud or Docker)
8. Implement monitoring and alerting

**Deployment Status**: Ready for local development, requires additional hardening for production deployment.
