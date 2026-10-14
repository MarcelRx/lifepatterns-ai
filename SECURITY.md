# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please report it responsibly:

1. **Do not** create a public issue
2. Email security details to: [security contact]
3. Include steps to reproduce the vulnerability
4. Allow time for the issue to be addressed before disclosure

## Security Practices

### Secret Management

- All secrets are stored in environment variables
- `.env` files are never committed to version control
- `.env.example` contains only placeholder values
- GitHub repository secrets are used for CI/CD and deployment
- Different secrets are used for development, staging, and production

### Cryptographic Configuration

**SECRET_KEY (JWT Signing):**

- Used for JWT token signing and session management
- Minimum 32 characters (64 hex characters recommended)
- Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- Rotation invalidates all existing tokens (users must re-authenticate)
- Never use placeholder values in production

**ENCRYPTION_KEY (Data Encryption - NOT IMPLEMENTED):**

- Currently NOT implemented in the application code
- Configuration variables exist in .env files but are not used
- Journal entries are stored in plaintext in PostgreSQL
- This is a planned feature for future implementation

### Database Security

- Parameterized queries throughout (SQL injection prevention)
- User isolation via `user_id` filtering
- PostgreSQL constraints on data ranges
- Foreign key constraints with CASCADE delete
- SSL mode configuration exists in .env files (DB_SSL_MODE) but is not currently enforced by the application code
- Future implementation should add SSL to the PostgreSQL connection string

### Password Security

- Bcrypt hashing with 12 rounds
- 72-byte password limit handling
- Native bcrypt library with passlib fallback
- Minimum 8-character password requirement
- No password storage in plaintext

### Configuration Validation

The application validates configuration at startup:

- Development mode: Warnings for missing/invalid configuration
- Production mode: Fails with clear error messages
- Rejects known insecure placeholders
- Validates SECRET_KEY length and format
- Checks for placeholder API keys

## Credential Rotation

### SECRET_KEY Rotation

1. Generate new key: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Update environment variable in production
3. Update GitHub repository secret
4. **Impact:** All existing JWT tokens become invalid
5. Users will need to re-authenticate on next login
6. Consider notifying users in advance

### Database Credentials Rotation

1. Create new database user with strong password
2. Grant necessary privileges to new user
3. Update application configuration
4. Update GitHub repository secret
5. Test connection with new credentials
6. Revoke old user access after verification

### Groq API Key Rotation

1. Log in to https://console.groq.com/keys
2. Generate new API key
3. Update application configuration
4. Update GitHub repository secret
5. Test AI features with new key
6. Revoke old key after verification

### ENCRYPTION_KEY Rotation

**Not applicable** - encryption is not currently implemented. No data migration required.

## Security Checklist

Before deploying to production:

- [ ] Generate unique SECRET_KEY (not used in development)
- [ ] Set ENVIRONMENT=production
- [ ] Configure database with strong password
- [ ] Configure GitHub repository secrets
- [ ] Review and rotate any exposed credentials
- [ ] Configure backup strategy
- [ ] Review database access controls
- [ ] Test configuration validation in production mode
- [ ] Verify no hardcoded secrets in codebase

## Notes

- **DEBUG and DB_SSL_MODE** are defined in .env files but not currently used in the application code
- **ENCRYPT_DATA and ENCRYPTION_KEY** are documented but encryption is not implemented

## Incident Response

If credentials are exposed:

1. **Immediate Actions:**
   - Rotate all exposed credentials immediately
   - Revoke API keys through provider dashboards
   - Change database passwords
   - Generate new SECRET_KEY

2. **Investigation:**
   - Determine scope of exposure
   - Review access logs
   - Identify affected users/data
   - Document timeline

3. **Remediation:**
   - Update all configuration files
   - Update GitHub repository secrets
   - Force user password resets if appropriate
   - Re-encrypt data if encryption key was exposed

4. **Prevention:**
   - Review secret management practices
   - Implement additional validation
   - Add security monitoring
   - Update documentation

## Dependencies

- Keep dependencies up to date
- Monitor security advisories
- Use `pip-audit` or similar tools
- Review dependency licenses

## Additional Resources

- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/secrets.html)
- [PostgreSQL Security Documentation](https://www.postgresql.org/docs/current/security.html)
