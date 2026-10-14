# GitHub Repository Secrets Mapping

This document maps application environment variables to GitHub repository secrets for deployment and CI/CD.

## Production Secrets

These secrets must be configured in GitHub repository settings for production deployment:

| Variable            | GitHub Secret Name    | Required | Purpose                                                                                          |
| ------------------- | --------------------- | -------- | ------------------------------------------------------------------------------------------------ |
| SECRET_KEY          | `SECRET_KEY`          | Yes      | JWT token signing key. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| DB_HOST             | `DB_HOST`             | Yes\*    | PostgreSQL database host (\* unless using DATABASE_URL)                                          |
| DB_PORT             | `DB_PORT`             | Yes\*    | PostgreSQL database port (\* unless using DATABASE_URL)                                          |
| DB_NAME             | `DB_NAME`             | Yes\*    | PostgreSQL database name (\* unless using DATABASE_URL)                                          |
| DB_USER             | `DB_USER`             | Yes\*    | PostgreSQL database user (\* unless using DATABASE_URL)                                          |
| DB_PASSWORD         | `DB_PASSWORD`         | Yes\*    | PostgreSQL database password (\* unless using DATABASE_URL)                                      |
| DATABASE_URL        | `DATABASE_URL`        | Yes\*    | Full PostgreSQL connection URL (alternative to individual DB\_\* variables)                      |
| GROQ_API_KEY        | `GROQ_API_KEY`        | No       | Groq API key for AI features. Get from: https://console.groq.com/keys                            |
| OPENWEATHER_API_KEY | `OPENWEATHER_API_KEY` | No       | OpenWeatherMap API key for weather correlation (feature not yet implemented)                     |

**Note:** Either provide `DATABASE_URL` OR the individual `DB_*` variables, not both.

## CI/CD Secrets

These secrets are used by GitHub Actions for automated testing:

| Variable        | GitHub Secret Name | Purpose                                     |
| --------------- | ------------------ | ------------------------------------------- |
| (None required) | -                  | CI workflow uses hardcoded test credentials |

The CI workflow uses these test-only values (hardcoded in `.github/workflows/ci.yml`):

- DB_HOST: localhost
- DB_PORT: 5432
- DB_NAME: test_db
- DB_USER: test_user
- DB_PASSWORD: test_password
- SECRET_KEY: test-secret-key-for-ci

These are not production secrets and are safe to use in CI.

## GitHub Environment Secrets (Recommended)

For production deployments, use GitHub Environments to separate secrets:

### Environment: `production`

- All production secrets listed above
- Deploy protection rules can be configured
- Required reviewers for deployment

### Environment: `staging` (optional)

- Staging database credentials
- Staging API keys
- Test SECRET_KEY

## Setup Instructions

### Option 1: Repository Secrets (Simple)

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret from the Production Secrets table above
4. Update workflow files to reference: `${{ secrets.SECRET_KEY }}`, etc.

### Option 2: Environment Secrets (Recommended)

1. Go to repository Settings → Environments
2. Create environment named "production"
3. Add secrets to the production environment
4. Configure deployment protection rules (optional)
5. Update workflow files to use environment: `environment: production`

## Workflow References

In `.github/workflows/ci.yml` and any deployment workflows, reference secrets like:

```yaml
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  DB_HOST: ${{ secrets.DB_HOST }}
  DB_PORT: ${{ secrets.DB_PORT }}
  DB_NAME: ${{ secrets.DB_NAME }}
  DB_USER: ${{ secrets.DB_USER }}
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
  GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
```

## Security Notes

- Never commit actual secret values to the repository
- Rotate secrets regularly (especially SECRET_KEY)
- Use different secrets for staging and production
- Grant least-privilege access to GitHub Actions
- Enable branch protection rules before deploying to production
- Review access logs regularly

## Credential Rotation

If secrets are compromised or need rotation:

1. Generate new secret values
2. Update GitHub repository secrets
3. Update environment variables in production deployment
4. For SECRET_KEY rotation: existing JWT tokens will become invalid; users will need to re-authenticate
5. For database credentials: rotate through database provider or administration interface
6. For API keys: rotate through provider dashboards (Groq, OpenWeatherMap)

## Notes

- **ENCRYPTION_KEY** is documented but not currently implemented in the application code
- Journal entries are stored in plaintext in PostgreSQL
- Data encryption is a planned feature for future implementation
