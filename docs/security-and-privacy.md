# Security and Privacy Documentation

## Purpose and Scope

This document describes the security and privacy controls implemented in LifePatterns AI, including authentication, authorization, input validation, secret management, data handling, and privacy considerations. It also identifies known limitations and provides practical recommendations.

**Scope:**

- Security-relevant application boundaries
- Authentication and authorization implementation
- Input validation and output handling
- Secret and environment-variable management
- External API and third-party service data transfers
- Logging and sensitive-data exposure risks
- Data storage, retention, and deletion behavior
- Dependency and supply-chain risks
- Relevant security tests and existing controls
- Privacy limitations and outstanding risks
- Practical recommendations

## Security-Relevant Application Boundaries

### Authentication Boundary

**Purpose**: Separate authenticated users from unauthenticated access

**Implementation**:

- Location: `login/auth.py`, `login/auth_page.py`
- Method: JWT tokens with session state management
- Boundary: Streamlit session state (`st.session_state.authenticated`)

**Security Measures**:

- Password hashing with bcrypt (12 rounds)
- JWT tokens with 30-day expiration
- Session state managed by Streamlit (server-side)
- Password requirements (minimum 8 characters)
- Username requirements (minimum 3 characters)

**Known Limitations**:

- No rate limiting on authentication endpoints
- No account lockout after failed login attempts
- No email verification for user registration
- No two-factor authentication
- No audit logging for authentication events

### Data Isolation Boundary

**Purpose**: Ensure users can only access their own data

**Implementation**:

- Location: `utils/database.py` (all database functions)
- Method: All database queries include `user_id` filter
- Boundary: Application-level filtering (not database-level RLS)

**Security Measures**:

- Parameterized queries (SQL injection prevention)
- User isolation via `user_id` filtering on all queries
- Foreign key constraints with CASCADE delete
- CHECK constraints on data ranges (mood 1-10, energy 1-10)

**Known Limitations**:

- No database-level row-level security (RLS)
- Relies on application-level enforcement (developer error could bypass)
- No audit logging for data access

### External API Boundary

**Purpose**: Control and monitor external API usage

**Implementation**:

- Location: `models/nlp_processor.py`, `models/forecast_engine.py`, `models/recommendation_engine.py`
- Method: Groq API calls via Python SDK
- Boundary: API key authentication, automatic fallback on failure

**Security Measures**:

- API key stored in environment variable (not in code)
- Automatic fallback to local processing on API failure
- No sensitive data sent beyond journal text and aggregated statistics
- HTTPS connection (handled by Groq SDK)

**Known Limitations**:

- No rate limiting on API calls
- No API usage monitoring or alerting
- No cost monitoring or budget controls
- API key rotation not automated

## Authentication and Authorization

### Authentication Implementation

**Location**: `login/auth.py`, class `AuthManager`

**Methods**:

- `register_user(username, password, email)`: User registration
- `authenticate_user(username, password)`: User login
- `create_access_token(user_id, username)`: JWT token generation
- `change_password(user_id, old_password, new_password)`: Password change
- `delete_user(user_id, password)`: Account deletion

### Password Security

**Hashing Algorithm**: Bcrypt with 12 rounds

**Implementation Details**:

- Location: `login/auth.py`, methods `_hash_password()` and `_verify_password()`
- Native bcrypt library with passlib fallback
- 72-byte password limit handling with truncation
- Minimum password length: 8 characters

**Password Hashing Code**:

```python
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)
```

**Security Strengths**:

- Bcrypt is a strong, slow hashing algorithm (resistant to brute force)
- 12 rounds provides good security/performance balance
- Fallback to passlib ensures compatibility

**Known Limitations**:

- No password complexity requirements beyond length
- No password history (prevent reuse)
- No password expiration policy
- No password strength meter in UI

### JWT Token Management

**JWT Configuration**:

- Algorithm: HS256 (HMAC with SHA-256)
- Secret: `SECRET_KEY` environment variable
- Expiration: 30 days
- Payload: user_id, username, exp, iat

**Implementation**: `login/auth.py`, method `create_access_token()`

**Security Strengths**:

- Standard JWT implementation with python-jose
- Expiration prevents indefinite token validity
- Signed with configurable secret key

**Known Limitations**:

- No token refresh mechanism
- No token revocation (except by changing SECRET_KEY)
- No token blacklist for compromised tokens
- 30-day expiration may be too long for sensitive applications

### Authorization Implementation

**Authorization Model**: User data isolation via `user_id` filtering

**Implementation**: All database functions require `user_id` parameter

**Example**:

```python
def get_entries(user_id: int, limit: int = 30) -> List[Entry]:
    # Parameterized query with user_id filter
    result = conn.execute(
        text("""
        SELECT entry_date, mood_rating, energy_level, sleep_hours, activities
        FROM daily_entries
        WHERE user_id = :user_id
        ORDER BY entry_date DESC
        LIMIT :limit
    """),
        {"user_id": user_id, "limit": limit},
    )
```

**Security Strengths**:

- Strict data isolation enforced at application level
- No cross-user data access possible if implemented correctly
- Parameterized queries prevent SQL injection

**Known Limitations**:

- No role-based access control (RBAC)
- No admin role or elevated permissions
- No resource-level permissions (all user data accessible to user)
- Relies on developer discipline to include `user_id` in all queries

## Input Validation and Output Handling

### Input Validation

**Client-Side Validation** (Streamlit UI):

- Mood: Slider constrained to 1-10 range
- Energy: Slider constrained to 1-10 range
- Sleep: Number input constrained to 0.0-12.0 range
- Activities: Multi-select from predefined list (13 options)
- Date: Date picker (no validation beyond date format)

**Server-Side Validation**:

- Journal text: Non-empty check (`if not journal.strip()`)
- Username: Minimum 3 characters, case-insensitive uniqueness
- Email: Optional, must be unique if provided
- Password: Minimum 8 characters

**Database-Level Validation**:

- CHECK constraints: mood_rating (1-10), energy_level (1-10)
- UNIQUE constraints: username, email, (user_id, entry_date)
- FOREIGN KEY constraints: Referential integrity
- NOT NULL constraints: Required fields

**Known Limitations**:

- No validation of data reasonableness (e.g., sleep = 25 hours rejected by UI but could be bypassed)
- No cross-field validation (e.g., mood vs sentiment consistency)
- No validation of journal text length or content
- No HTML sanitization (not needed, no rich text input)
- No profanity filtering
- No personal information redaction

### Output Handling

**Output Encoding**:

- Streamlit handles HTML encoding automatically
- No manual output encoding required
- No XSS vulnerabilities expected (no user-controlled HTML rendering)

**Data Export**:

- Format: JSON
- Scope: All entries for authenticated user
- User-triggered via download button
- No sensitive data added beyond what user entered

**Known Limitations**:

- No data redaction in export (includes all journal text, email if provided)
- No export logging or audit trail
- No export rate limiting

## Secret and Environment-Variable Management

### Environment Variables

**Required Variables**:

- `SECRET_KEY`: JWT token signing key
- Database connection: `DATABASE_URL` OR `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

**Optional Variables**:

- `GROQ_API_KEY`: Groq API key for AI features
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key (feature not implemented)

**Configuration Files**:

- `.env.example`: Local development template
- `.env.production.example`: Production deployment template
- `.env.test`: CI/CD testing configuration

### Secret Validation

**Implementation**: `utils/config.py`

**Validation Rules**:

- SECRET_KEY must be at least 32 characters
- SECRET_KEY cannot be known insecure placeholders (e.g., "your-secret-key-here")
- Production mode fails on missing or invalid configuration
- Development mode shows warnings but continues

**Validation Code**:

```python
def validate_secret_key(secret_key: str) -> bool:
    insecure_placeholders = [
        "your-secret-key-here",
        "your-secret-key-here-change-in-production",
        # ... more placeholders
    ]
    if secret_key.lower() in [p.lower() for p in insecure_placeholders]:
        if environment == "production":
            raise ConfigError("SECRET_KEY is using a placeholder value")
    if len(secret_key) < 32:
        if environment == "production":
            raise ConfigError(f"SECRET_KEY is too short ({len(secret_key)} chars)")
    return True
```

**Security Strengths**:

- Prevents accidental use of placeholder values in production
- Enforces minimum length for SECRET_KEY
- Clear error messages for configuration issues

**Known Limitations**:

- No automatic SECRET_KEY generation
- No SECRET_KEY rotation mechanism
- No validation of database password strength
- No validation of API key format

### Secret Storage

**Development**:

- Stored in `.env` file (not committed to git)
- `.env` in `.gitignore`

**Production**:

- Should be stored in environment variables or secret management service
- Streamlit Cloud: Configured in secrets dashboard
- GitHub Actions: Configured in repository secrets
- Docker: Passed as environment variables (not in .env file)

**Security Strengths**:

- `.env` in `.gitignore` prevents accidental commits
- Example files provided with placeholder values
- CI/CD uses test-only credentials (not production secrets)

**Known Limitations**:

- No secret rotation automation
- No secret versioning or history
- No secret sharing mechanism for team collaboration
- No audit logging for secret access

### Secret Scanning

**Tool**: Gitleaks

**Configuration**: `.gitleaks.toml`

**Purpose**: Detect hardcoded secrets in committed files

**CI/CD Integration**: GitHub Actions workflow executes Gitleaks on push/PR

**Allowlist**:

- Example environment files (`.env.example`, `.env.production.example`, `.env.test`)
- Placeholder values (e.g., "your-password-here")
- Test credentials (e.g., "test_password")
- Documentation comments

**Security Strengths**:

- Automated secret detection in CI/CD
- Prevents accidental secret commits
- Custom configuration for project-specific patterns

**Known Limitations**:

- Only scans committed files (not local uncommitted changes)
- May have false positives (handled by allowlist)
- Does not prevent secrets from being added, only detects them after commit

## External API and Third-Party Service Data Transfers

### Groq API

**Purpose**: AI-powered NLP analysis and recommendations

**Activation Condition**: `ENABLE_EXTERNAL_AI=true` (operator configuration) AND `GROQ_API_KEY` is set AND user explicitly opts in via UI checkbox

**Privacy Control**: External AI is disabled by default (`ENABLE_EXTERNAL_AI=false`). Journal text is transmitted to Groq only when:

1. Operator has enabled external AI via `ENABLE_EXTERNAL_AI=true`
2. User has explicitly checked the consent checkbox in the Daily Input form
3. A valid `GROQ_API_KEY` is configured

If any of these conditions is false, the application uses local TextBlob/keyword-based analysis only, and no data is sent to Groq.

**Data Sent to Groq**:

- Journal text content (plaintext)
- Aggregated statistics (mood averages, pattern names) for recommendations

**Data Received from Groq**:

- Sentiment analysis results (JSON)
- Emotion scores (JSON)
- Keywords and topics (JSON)
- AI-generated insights (JSON)

**Authentication**: API key via environment variable

**Transfer Security**: HTTPS (handled by Groq SDK)

**Secure-by-Default Configuration**: External AI is disabled by default (`ENABLE_EXTERNAL_AI=false`). Requires explicit operator configuration AND user consent before any data is transmitted to Groq.

**Data Retention by Groq**: Governed by Groq's data retention policy (not controlled by application)

**Security Strengths**:

- HTTPS encryption in transit
- API key not exposed in code
- Automatic fallback to local processing on API failure
- No sensitive user credentials sent to Groq

**Known Limitations**:

- No control over Groq's data retention or processing
- No audit logging of API calls
- No cost monitoring or budget controls
- No rate limiting on API calls
- API key rotation not automated

### OpenWeatherMap API

**Status**: Documented but not implemented

**Purpose**: Weather correlation analysis (planned feature)

**Current State**: API key configuration exists in `.env` files but not used in code

**Security Implications**: None (not actively used)

## Logging and Sensitive-Data Exposure Risks

### Current Logging Implementation

**Logging Approach**: Print statements to console

**Locations**:

- Error logging in database operations: `print(f"Error saving entry: {e}")`
- AI failure logging: `print(f"AI analysis failed, using local fallback: {e}")`
- Configuration validation logging: `print(f"Configuration validation warning: {e}")`

**Security Strengths**:

- No sensitive data logged (error messages generic)
- Print statements only in development/production console (not exposed to users)

**Known Limitations**:

- No structured logging framework (e.g., logging module)
- No log levels (DEBUG, INFO, WARNING, ERROR)
- No log rotation or retention policy
- No centralized logging
- No audit logging for sensitive operations (authentication, data access, account deletion)
- Error messages may contain stack traces in development mode

### Sensitive Data Exposure Risks

**Potentially Sensitive Data**:

- Journal text (may contain personal information)
- Email addresses (if provided)
- Password hashes (stored in database, not exposed in logs)

**Exposure Risks**:

- **Database breach**: Journal text stored in plaintext (no encryption at rest)
- **Log exposure**: Stack traces may expose file paths or variable names in development
- **API exposure**: Journal text sent to Groq API (HTTPS encrypted)
- **Export exposure**: JSON export includes all journal text and email

**Mitigations**:

- Parameterized queries prevent SQL injection
- No secrets in committed code
- `.env` in `.gitignore`
- Gitleaks secret scanning in CI/CD

**Missing Mitigations**:

- No encryption at rest for journal text or email
- No audit logging for data access
- No data loss prevention (DLP)
- No monitoring for unauthorized data access

## Data Storage, Retention, and Deletion Behavior

### Data Storage

**Storage Technology**: PostgreSQL 15

**Data Encryption at Rest**: **Not implemented**

- Journal text stored as plaintext TEXT
- Email addresses stored as plaintext VARCHAR
- Password hashes stored as VARCHAR (bcrypt-hashed)
- `ENCRYPT_DATA` and `ENCRYPTION_KEY` environment variables documented but not used

**Database SSL**: **Documented but not enforced**

- `DB_SSL_MODE` environment variable exists
- Not currently enforced by application code
- Future implementation should add SSL to PostgreSQL connection string

**Security Strengths**:

- Passwords hashed with bcrypt (not reversible)
- ACID transactions ensure data integrity
- Foreign key constraints prevent orphaned data

**Known Limitations**:

- No encryption at rest for sensitive data (journal text, email)
- No database SSL enforcement
- No field-level encryption
- No data masking for sensitive fields

### Data Retention

**Retention Policy**: **Not implemented**

- No automated data expiration
- No data archival
- No data retention schedule
- User data persists indefinitely until account deletion

**User Control**:

- Users can delete their account (CASCADE delete removes all data)
- Users can export all their data via JSON download
- No data retention controls in UI

**Security Strengths**:

- User can delete all data on account deletion
- CASCADE delete ensures no orphaned data

**Known Limitations**:

- No automated data cleanup
- No data retention policy (legal/regulatory compliance)
- No data archival for long-term storage
- No data anonymization

### Data Deletion

**Account Deletion**:

- Location: `login/auth.py`, method `delete_user()`
- Requires password verification
- CASCADE delete removes all related data (entries, patterns, recommendations)
- No soft delete or archival

**Entry Deletion**:

- No individual entry deletion (UPSERT allows update but not delete)
- Only account-level deletion available

**Security Strengths**:

- Password verification required for account deletion
- CASCADE delete ensures complete data removal
- No residual data after deletion

**Known Limitations**:

- No undo for account deletion
- No data recovery mechanism
- No deletion audit log
- No retention of deleted data for compliance

## Dependency and Supply-Chain Risks

### Python Dependencies

**Dependency Management**: `requirements.txt` with pinned versions

**Security Updates**: No automated dependency scanning or updating

**Vulnerability Scanning**: Not implemented

**Known Tools** (not configured):

- `pip-audit`: Check for known vulnerabilities
- `safety`: Check for security issues
- `dependabot`: GitHub dependency monitoring (not configured)

**Recommendations**:

- Implement regular dependency updates
- Add vulnerability scanning to CI/CD
- Use tools like `pip-audit` or `safety`
- Enable GitHub Dependabot

### External Services

**Groq API**:

- Dependency on external service availability
- No SLA guarantee
- Potential for API changes or deprecation
- Cost implications (pay-per-use)

**Mitigations**:

- Automatic fallback to local TextBlob processing
- No hard dependency on Groq for core functionality

**Known Limitations**:

- No API versioning in code
- No monitoring for API degradation
- No budget controls or cost alerts

## Relevant Security Tests and Existing Controls

### Implemented Security Controls

1. **Password Hashing**: Bcrypt with 12 rounds
2. **SQL Injection Prevention**: Parameterized queries throughout
3. **Data Isolation**: User-level filtering on all queries
4. **Secret Validation**: Configuration validation at startup
5. **Secret Scanning**: Gitleaks in CI/CD
6. **Input Validation**: Client-side and server-side validation
7. **Constraint Enforcement**: Database CHECK and UNIQUE constraints
8. **Cascading Deletes**: Foreign key CASCADE delete on user deletion

### Security Tests

**Status**: **No dedicated security tests**

**Missing Security Tests**:

- No tests for SQL injection attempts
- No tests for authentication bypass attempts
- No tests for authorization bypass (cross-user data access)
- No tests for input validation bypass
- No tests for XSS attempts
- No tests for CSRF attempts (not applicable for Streamlit)
- No penetration testing
- No dependency vulnerability scanning

**Recommendations**:

- Add security-focused unit tests
- Implement automated dependency vulnerability scanning
- Consider periodic penetration testing
- Add security linting (e.g., bandit)

## Privacy Limitations and Outstanding Risks

### Privacy Limitations

**Data Collection**:

- Journal text may contain personal information (no redaction)
- Email addresses optional but stored in plaintext
- No consent mechanism for data collection
- No privacy policy displayed to users

**Data Processing**:

- Journal text sent to Groq API (external processing)
- No control over Groq's data handling
- No opt-out for AI processing

**Data Storage**:

- No encryption at rest for journal text or email
- No data anonymization
- No data minimization (all data stored as entered)

**Data Sharing**:

- No data sharing with third parties (except Groq API)
- No cross-user data sharing
- No public data exposure

**User Rights**:

- Users can export all their data
- Users can delete their account and all data
- No data access request mechanism beyond export
- No data correction mechanism beyond account settings

### Outstanding Risks

**High Priority**:

1. **No encryption at rest**: Journal text and email stored in plaintext
2. **No database SSL**: DB_SSL_MODE documented but not enforced
3. **No audit logging**: No logging of authentication, data access, or deletion events
4. **No rate limiting**: Authentication endpoints not rate-limited
5. **No account lockout**: Failed login attempts not tracked

**Medium Priority**: 6. **No two-factor authentication**: Only password-based authentication 7. **No email verification**: User registration does not require email verification 8. **No secret rotation**: No automated SECRET_KEY or API key rotation 9. **No dependency scanning**: No automated vulnerability scanning 10. **No security tests**: No dedicated security testing

**Low Priority**: 11. **No audit logging for data export**: No tracking of data exports 12. **No data retention policy**: No automated data cleanup 13. **No monitoring**: No monitoring for unauthorized access or anomalies 14. **No backup security**: No documented backup encryption or access controls

## Practical Recommendations

### Immediate Improvements (High Priority)

1. **Implement Encryption at Rest**:
   - Encrypt journal text using `ENCRYPTION_KEY` (already documented)
   - Encrypt email addresses
   - Use database-level encryption or application-level encryption

2. **Enforce Database SSL**:
   - Add SSL mode to PostgreSQL connection string
   - Use `DB_SSL_MODE` environment variable
   - Require SSL in production mode

3. **Add Audit Logging**:
   - Log authentication events (login, logout, failed attempts)
   - Log data access (user_id, timestamp, operation)
   - Log sensitive operations (password change, account deletion)
   - Use structured logging framework (logging module)

4. **Implement Rate Limiting**:
   - Add rate limiting to authentication endpoints
   - Track failed login attempts
   - Implement account lockout after N failed attempts

5. **Add Email Verification**:
   - Require email verification for registration
   - Send verification email with token
   - Prevent account usage until verified

### Medium-Term Improvements (Medium Priority)

6. **Implement Two-Factor Authentication**:
   - Add TOTP (Time-based One-Time Password) support
   - Use library like pyotp
   - Make 2FA optional for users

7. **Automate Secret Rotation**:
   - Implement SECRET_KEY rotation mechanism
   - Schedule regular API key rotation
   - Document rotation procedure

8. **Add Dependency Vulnerability Scanning**:
   - Integrate `pip-audit` or `safety` into CI/CD
   - Enable GitHub Dependabot
   - Implement regular dependency updates

9. **Add Security Tests**:
   - Add tests for SQL injection attempts
   - Add tests for authentication bypass
   - Add tests for authorization bypass
   - Use security linting tool (bandit)

10. **Implement Monitoring**:
    - Add application performance monitoring
    - Add security event monitoring
    - Set up alerts for suspicious activity

### Long-Term Improvements (Low Priority)

11. **Implement Data Retention Policy**:
    - Define data retention periods
    - Implement automated data cleanup
    - Add data archival for long-term storage

12. **Add Data Anonymization**:
    - Implement data masking for sensitive fields
    - Add anonymization for analytics
    - Consider differential privacy techniques

13. **Conduct Security Audit**:
    - Perform penetration testing
    - Conduct code review for security issues
    - Review compliance with security standards (OWASP)

14. **Implement Backup Security**:
    - Encrypt database backups
    - Secure backup storage access
    - Document backup restoration procedure

## Compliance Considerations

### GDPR (General Data Protection Regulation)

**Status**: **Not compliant**

**Missing Elements**:

- No explicit consent mechanism for data collection
- No privacy policy
- No data retention policy
- No data processing records
- No data breach notification procedure
- No Data Protection Officer (DPO)
- No right to be forgotten beyond account deletion

**Recommendations**:

- Implement consent mechanism
- Create and display privacy policy
- Implement data retention policy
- Document data processing activities
- Create breach notification procedure

### HIPAA (Health Insurance Portability and Accountability Act)

**Status**: **Not applicable** (not a healthcare application)

**Note**: Application tracks mood and wellbeing but is not a healthcare tool. If positioning as healthcare tool, HIPAA compliance would be required.

### SOC 2 (Service Organization Control 2)

**Status**: **Not compliant**

**Missing Elements**:

- No security incident response plan
- No access control policies
- No change management procedures
- No monitoring and logging
- No vulnerability management program

**Recommendations**:

- If targeting enterprise customers, consider SOC 2 compliance
- Implement security governance framework

## Conclusion

LifePatterns AI implements basic security controls including password hashing, SQL injection prevention, user data isolation, and secret validation. However, significant security gaps exist, particularly in encryption at rest, audit logging, rate limiting, and security testing.

**Strengths**:

- Password hashing with bcrypt
- SQL injection prevention via parameterized queries
- User data isolation at application level
- Secret validation and placeholder detection
- Secret scanning in CI/CD
- Automatic fallback for external API failures

**Critical Gaps**:

- No encryption at rest for journal text or email
- No database SSL enforcement
- No audit logging for security events
- No rate limiting on authentication
- No account lockout after failed attempts
- No two-factor authentication
- No email verification for registration
- No security tests

**Priority Actions**:

1. Implement encryption at rest for sensitive data
2. Enforce database SSL connections
3. Add audit logging for security events
4. Implement rate limiting and account lockout
5. Add email verification for registration
6. Implement dependency vulnerability scanning
7. Add security-focused tests

**Privacy Considerations**:

- Journal text may contain personal information (no redaction)
- Data sent to external API (Groq) with no control over retention
- No encryption at rest
- No data retention policy
- Users can export and delete data, but no other privacy controls

**Recommendation**: Treat this as a personal/non-sensitive application. If positioning for production use with sensitive data, implement the critical security gaps listed above.
