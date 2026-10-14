# Architecture Documentation

## Purpose and Scope

This document describes the architectural design of LifePatterns AI, a Streamlit-based personal behavior analytics application. The architecture follows a layered design with clear separation between presentation, business logic, data access, and external services.

**Scope:**

- Application structure and component organization
- Module boundaries and responsibilities
- Data flow between components
- External dependencies and integrations
- Runtime execution patterns
- Error handling strategies
- Current architectural limitations

## Architectural Style

LifePatterns AI follows a **layered architecture** with the following characteristics:

- **Monolithic application**: All functionality runs within a single Streamlit application
- **Separation of concerns**: Distinct layers for UI, business logic, data access, and external services
- **Functional decomposition**: Modules organized by domain (authentication, NLP, patterns, forecasting)
- **Database-centric**: PostgreSQL as the single source of truth for persistent data
- **Stateless business logic**: No in-memory state in business logic components (state managed by Streamlit session)

The application is **not** microservices, event-driven, or serverless. It is designed for single-tenant deployment with user-level data isolation enforced at the database query level.

## Main Application Components

### 1. Frontend Layer (Streamlit)

**Location:** `app.py`, `pages/` directory

**Responsibilities:**

- User interface rendering and interaction
- Session state management (authentication, user data)
- Page routing and navigation
- Form input validation and submission
- Display of visualizations and analytics

**Key Files:**

- `app.py`: Main application entry point, authentication flow, page routing
- `pages/Daily_Input.py`: Daily journal entry form
- `pages/Pattern_Discovery.py`: Pattern analysis and visualization
- `pages/Outcome_Forecast.py`: Wellbeing forecasting interface
- `pages/Daily_Insights.py`: Personalized recommendations display
- `pages/reports_view.py`: Historical reports and data export

**Runtime Behavior:**

- Streamlit re-executes the entire script on every user interaction
- Session state (`st.session_state`) persists across re-executions
- Authentication state stored in session state (authenticated flag, user object, JWT token)

**Dependencies:**

- Streamlit 1.28.0
- streamlit-option-menu 0.3.6

### 2. Authentication Layer

**Location:** `login/auth.py`, `login/auth_page.py`

**Responsibilities:**

- User registration with validation
- User authentication (login) with password verification
- JWT token generation and validation
- Password change functionality
- Account deletion with verification

**Key Files:**

- `login/auth.py`: `AuthManager` class with authentication methods
- `login/auth_page.py`: Login and registration UI pages

**Implementation Details:**

- Password hashing using bcrypt (12 rounds) with passlib fallback
- JWT tokens with HS256 algorithm, 30-day expiration
- User data class for session state management
- Minimum password length: 8 characters
- Minimum username length: 3 characters

**Security Features:**

- Parameterized database queries (SQL injection prevention)
- Bcrypt 72-byte password limit handling with truncation
- Case-insensitive username/email lookup
- Unique constraints on username and email

**Dependencies:**

- python-jose 3.3.0 (JWT)
- passlib 1.7.4 (bcrypt)
- cryptography 41.0.7

### 3. NLP Processing Layer

**Location:** `models/nlp_processor.py`

**Responsibilities:**

- Sentiment analysis of journal entries
- Emotion detection (joy, sadness, anger, fear, stress, calm)
- Keyword extraction
- Topic classification
- Summary generation
- Behavioral insights generation

**Key Files:**

- `models/nlp_processor.py`: `NLPProcessor` class with analysis methods

**Implementation Details**:

- **Primary**: Groq API (Llama-3.1-8b-instant) for AI-powered analysis (when `ENABLE_EXTERNAL_AI=true`, `GROQ_API_KEY` set, AND user explicitly opts in via UI checkbox)
- **Fallback**: TextBlob for local sentiment analysis when Groq unavailable, disabled, or consent not granted
- **Tertiary**: Keyword-based sentiment calculation if TextBlob unavailable
- Structured JSON output format from Groq API
- Temperature: 0.3 for consistent results
- Max tokens: 500 for journal analysis, 200-300 for recommendations
- **Privacy Control**: External AI is disabled by default (`ENABLE_EXTERNAL_AI=false`). Requires both operator configuration (`ENABLE_EXTERNAL_AI=true`) AND explicit user consent via UI checkbox. Journal text is transmitted to Groq only when both conditions are satisfied.

**Error Handling:**

- Automatic fallback to local analysis on Groq API failure
- Graceful degradation with default values for missing fields
- Empty input handling returns neutral results

**Dependencies:**

- groq 0.4.2
- textblob 0.17.1
- nltk 3.8.1

### 4. Pattern Detection Layer

**Location:** `models/pattern_detector.py`

**Responsibilities:**

- Mood trend detection (improving/declining/stable)
- Sleep-mood correlation analysis
- Activity impact identification
- Pattern aggregation and confidence scoring

**Key Files:**

- `models/pattern_detector.py`: `PatternDetector` class with detection methods

**Implementation Details:**

- **Mood trend**: Compares average mood of first half vs second half of entries, threshold > 0.5
- **Sleep-mood correlation**: Compares average mood for good sleep (7h+) vs poor sleep (<6h), threshold > 1 point difference
- **Activity impact**: Identifies activity with highest average mood (minimum 2 data points, mood > 6)
- Minimum data requirements: 3 entries for mood trend, 5 entries for sleep correlation, 2 entries per activity
- Confidence scores calculated based on change magnitude

**Limitations:**

- No statistical significance testing
- No time-aware analysis (all entries treated equally)
- No seasonal or periodic pattern detection
- Assumes linear relationships

**Dependencies:**

- No external ML libraries (pure Python statistical analysis)

### 5. Forecast Engine Layer

**Location:** `models/forecast_engine.py`

**Responsibilities:**

- Current wellbeing status assessment
- Trajectory prediction (improving/declining/stable)
- Risk assessment (mood decline, depression risk, burnout risk)
- 7-day mood forecasting
- Intervention suggestion
- AI-powered forecast insights (optional)

**Key Files:**

- `models/forecast_engine.py`: `ForecastEngine` class with forecasting methods

**Implementation Details:**

- **Status assessment**: Based on recent 3 entries average (mood >= 7, energy >= 6 = Thriving)
- **Trajectory prediction**: Linear extrapolation from first half to second half of data, threshold > 0.5
- **Risk assessment**: Rule-based checks for declining trends, low mood streaks, sleep deprivation
- **7-day forecast**: Linear extrapolation with decreasing confidence over time (0.9 to 0.5)
- **Interventions**: Rule-based recommendations based on trajectory direction
- **AI insights**: Optional Groq API call for personalized forecast context

**Limitations:**

- No machine learning models for prediction
- Linear extrapolation assumes constant trend
- No confidence intervals or uncertainty quantification
- No seasonal adjustment
- Forecast accuracy not validated

**Dependencies:**

- groq 0.4.2 (optional, for AI insights)

### 6. Recommendation Engine Layer

**Location:** `models/recommendation_engine.py`

**Responsibilities:**

- Mood-based recommendations
- Sleep-based recommendations
- Activity-based recommendations
- AI-powered personalized recommendations (optional)

**Key Files:**

- `models/recommendation_engine.py`: `RecommendationEngine` class with generation methods

**Implementation Details:**

- **Mood recommendations**: Based on detected mood trend patterns
- **Sleep recommendations**: Based on sleep-mood correlation or sleep deficit detection
- **Activity recommendations**: Based on positive activity impact patterns
- **AI recommendations**: Groq API call with recent data context (minimum 3 entries)
- Structured output with priority levels (high/medium/ongoing)
- Confidence scores based on pattern detection confidence

**Limitations:**

- No user feedback on recommendation quality
- No A/B testing of recommendation effectiveness
- No learning from user behavior
- Recommendations are rule-based with optional AI enhancement

**Dependencies:**

- groq 0.4.2 (optional, for AI recommendations)

### 7. Visualization Layer

**Location:** `components/visualizations.py`

**Responsibilities:**

- Mood and energy trend charts
- Activity impact bar charts
- Sleep-mood correlation scatter plots
- Sentiment timeline charts
- Weekly summary statistics

**Key Files:**

- `components/visualizations.py`: `Visualizations` class with chart generation methods

**Implementation Details:**

- Plotly 5.18.0 for interactive charts
- Dark theme styling (plotly_dark template)
- Pandas DataFrame for data preparation
- Rolling average trend lines (3-day window)
- Color coding based on mood thresholds (green >= 7, yellow >= 5, red < 5)
- OLS trend line for sleep-mood correlation

**Dependencies:**

- plotly 5.18.0
- pandas 2.1.3
- numpy 1.26.2

### 8. Database Layer

**Location:** `utils/database.py`, `data/database.py`

**Responsibilities:**

- Database connection management
- User data retrieval with isolation
- Entry creation and updates (UPSERT)
- User statistics aggregation
- Data export functionality

**Key Files:**

- `utils/database.py`: `get_engine()`, `get_entries()`, `save_entry()`, `get_user_stats()`, `get_all_entries_for_export()`
- `data/database.py`: Database connection testing utility
- `utils/setup_postgres.sql`: Database schema and setup script

**Implementation Details:**

- SQLAlchemy 2.0.23 ORM with raw SQL queries
- PostgreSQL 15 as database engine
- JSONB columns for flexible schema (emotions, settings, pattern_data)
- UPSERT operation for daily entries (INSERT ... ON CONFLICT DO UPDATE)
- Parameterized queries throughout (SQL injection prevention)
- User isolation enforced via `user_id` filter on all queries
- Foreign key constraints with CASCADE delete

**Data Entities:**

- `users`: User accounts, credentials, settings
- `daily_entries`: Journal entries with metrics and AI analysis
- `detected_patterns`: Identified behavioral patterns
- `recommendations`: Personalized recommendations

**Dependencies:**

- psycopg2-binary 2.9.9
- SQLAlchemy 2.0.23
- alembic 1.12.1 (installed but migrations not implemented)

### 9. Configuration Layer

**Location:** `utils/config.py`

**Responsibilities:**

- Environment variable loading and validation
- SECRET_KEY validation and generation
- Database configuration validation
- Production vs development mode behavior

**Key Files:**

- `utils/config.py`: Configuration validation functions

**Implementation Details:**

- python-dotenv 1.0.0 for environment variable loading
- Development mode: Warnings for missing/invalid configuration
- Production mode: Fails with clear error messages
- Rejects known insecure placeholders (e.g., "your-secret-key-here")
- SECRET_KEY minimum length validation (32 characters)
- Automatic temporary key generation in development mode

**Dependencies:**

- python-dotenv 1.0.0
- pydantic 2.5.2
- pydantic-settings 2.1.0

## Module and Service Boundaries

### Module Organization

```
lifepatterns-ai/
├── app.py                      # Application entry point
├── login/                      # Authentication module
│   ├── auth.py                 # AuthManager class
│   └── auth_page.py            # Login/registration UI
├── pages/                      # Page controllers
│   ├── Daily_Input.py
│   ├── Pattern_Discovery.py
│   ├── Outcome_Forecast.py
│   ├── Daily_Insights.py
│   └── reports_view.py
├── models/                     # Business logic
│   ├── nlp_processor.py        # NLP analysis
│   ├── pattern_detector.py     # Pattern detection
│   ├── forecast_engine.py      # Forecasting
│   ├── recommendation_engine.py # Recommendations
│   └── groq_client.py          # Groq API testing
├── components/                 # Reusable components
│   └── visualizations.py       # Chart generation
├── utils/                      # Utilities
│   ├── database.py             # Database operations
│   ├── config.py               # Configuration validation
│   └── setup_postgres.sql      # Database schema
└── data/                       # Data utilities
    └── database.py             # Connection testing
```

### Service Boundaries

**Authentication Service:**

- Boundary: User registration, login, password management
- Dependencies: Database layer, configuration layer
- External dependencies: None (local password hashing)

**NLP Service:**

- Boundary: Text analysis, sentiment, emotions, keywords
- Dependencies: Configuration layer
- External dependencies: Groq API (optional), TextBlob (local)

**Pattern Detection Service:**

- Boundary: Mood trends, correlations, activity impact
- Dependencies: Database layer (for entry data)
- External dependencies: None

**Forecast Service:**

- Boundary: Trajectory prediction, risk assessment, forecasting
- Dependencies: Pattern detection service, NLP service (optional)
- External dependencies: Groq API (optional)

**Recommendation Service:**

- Boundary: Personalized suggestions
- Dependencies: Pattern detection service, forecast service
- External dependencies: Groq API (optional)

**Visualization Service:**

- Boundary: Chart generation and data visualization
- Dependencies: None (stateless)
- External dependencies: None

## API and Integration Boundaries

### External API Integrations

**Groq API:**

- Purpose: AI-powered NLP analysis and recommendations
- Models: Llama-3.1-8b-instant (primary), Llama-3.3-70b-versatile (reasoning)
- Authentication: API key via environment variable (GROQ_API_KEY)
- Fallback: Local TextBlob analysis
- Error handling: Automatic fallback on API failure
- Rate limiting: Not implemented (relies on Groq's rate limits)

**Planned but Not Implemented:**

- OpenWeatherMap API (weather correlation) - documented but not integrated

### Internal API Boundaries

**Database Access:**

- All database access through `utils/database.py` functions
- No direct SQL in page controllers or business logic
- User isolation enforced at function level (user_id required parameter)

**NLP Processing:**

- All NLP operations through `models/nlp_processor.py`
- Direct Groq API calls only within NLP processor
- Fallback logic encapsulated within processor

**Pattern Detection:**

- All pattern detection through `models/pattern_detector.py`
- Entry data provided as input, no database access within detector

## External Dependencies and Services

### Third-Party Services

| Service        | Purpose             | Required             | Fallback         |
| -------------- | ------------------- | -------------------- | ---------------- |
| Groq API       | AI NLP analysis     | No                   | TextBlob (local) |
| PostgreSQL     | Data persistence    | Yes                  | None             |
| OpenWeatherMap | Weather correlation | No (not implemented) | N/A              |

### Python Dependencies

**Core Runtime:**

- Python 3.9+
- Streamlit 1.28.0
- python-dotenv 1.0.0

**Database:**

- psycopg2-binary 2.9.9
- SQLAlchemy 2.0.23
- alembic 1.12.1

**AI/NLP:**

- groq 0.4.2
- textblob 0.17.1
- nltk 3.8.1

**Data Processing:**

- pandas 2.1.3
- numpy 1.26.2
- python-dateutil 2.8.2

**Visualization:**

- plotly 5.18.0
- wordcloud 1.9.2

**Security:**

- cryptography 41.0.7
- python-jose[cryptography] 3.3.0
- passlib[bcrypt] 1.7.4

**Development:**

- pytest 7.4.3
- pytest-cov 4.1.0
- black 23.11.0
- flake8 6.1.0

**Optional:**

- redis 5.0.1 (caching, not used)
- scikit-learn 1.3.2 (installed but not actively used)

## Runtime Execution Flow

### Application Startup

1. Load environment variables from `.env` file
2. Validate configuration (warnings in development, errors in production)
3. Initialize Streamlit page configuration
4. Initialize session state (authenticated flag, user object, token)
5. Check authentication status
6. If authenticated: Show main app with navigation
7. If not authenticated: Show login page

### User Authentication Flow

```
User enters credentials → AuthManager.authenticate_user()
→ Database query for user → Password verification with bcrypt
→ JWT token generation → Session state update → Redirect to main app
```

### Daily Entry Submission Flow

```
User submits form → Text validation → NLP analysis (Groq or TextBlob)
→ save_entry() with user_id → Database UPSERT → Success/error feedback
```

### Pattern Discovery Flow

```
User navigates to Pattern Discovery → get_entries(user_id)
→ PatternDetector(entries) → detect_mood_trend(), detect_sleep_mood_correlation(), detect_activity_impact()
→ Visualizations(entries) → Chart generation → Display results
```

### Outcome Forecast Flow

```
User navigates to Outcome Forecast → get_entries(user_id)
→ PatternDetector(entries) → ForecastEngine(entries, patterns)
→ _assess_current_status(), _predict_trajectory(), _assess_risks(), _generate_predictions()
→ Optional AI forecast → Display forecast with interventions
```

## Error Handling and Failure Boundaries

### Error Handling Strategy

**Streamlit Layer:**

- Form validation errors displayed to user
- Try-except blocks around database operations
- Generic error messages for security (no stack traces to user)

**Authentication Layer:**

- Invalid credentials: Generic "Invalid username or password" message
- Registration errors: Specific validation messages (username length, password requirements)
- Database errors: Logged to console, generic error to user

**NLP Layer:**

- Groq API failure: Automatic fallback to TextBlob
- TextBlob unavailable: Fallback to keyword-based analysis
- Empty input: Returns neutral result structure
- Invalid JSON from Groq: Uses default values

**Pattern Detection Layer:**

- Insufficient data: Returns None (no pattern detected)
- Missing fields: Skips entries with missing required data
- Statistical thresholds: No errors, returns None if threshold not met

**Forecast Layer:**

- Insufficient data: Returns None (no forecast)
- AI forecast failure: Continues with rule-based forecast
- Calculation errors: Returns default/stable values

**Database Layer:**

- Connection errors: Returns False, logs error
- Query errors: Returns False, logs error
- Constraint violations: Database-level error handling

### Failure Boundaries

**User Isolation Failure:**

- Mitigation: All database functions require user_id parameter
- Risk: Developer error could bypass isolation
- Detection: Code review and testing

**External API Failure:**

- Mitigation: Fallback to local processing
- Risk: Reduced functionality without external API
- Detection: Graceful degradation with user notification

**Database Connection Failure:**

- Mitigation: Application displays error, prevents operation
- Risk: Application unusable without database
- Detection: Connection test at startup, retry logic not implemented

**Configuration Error:**

- Mitigation: Validation at startup with warnings (dev) or errors (prod)
- Risk: Application may start with invalid configuration in development
- Detection: Configuration validation in utils/config.py

## Architectural Constraints and Current Limitations

### Scalability Constraints

1. **Single-Process Execution**: Streamlit runs as a single process, no horizontal scaling
2. **Database Connection Pooling**: Not implemented (each query creates new connection)
3. **Caching**: Redis configured but not used (no caching layer)
4. **Background Processing**: No async job processing (all operations synchronous)

### Performance Limitations

1. **Streamlit Re-execution**: Entire script re-runs on every interaction
2. **NLP Latency**: Groq API calls add latency to entry submission
3. **No Query Optimization**: No database indexes beyond basic setup
4. **No Pagination**: All entries loaded into memory (limit 30 by default)

### Security Limitations

1. **No Rate Limiting**: Authentication endpoints not rate-limited
2. **No Account Lockout**: Failed login attempts not tracked
3. **No Email Verification**: User registration does not require email verification
4. **No Two-Factor Authentication**: Only password-based authentication
5. **No Audit Logging**: Sensitive operations not logged
6. **Data Encryption**: Not implemented (journal entries stored in plaintext)
7. **Database SSL**: Documented but not enforced by application code

### Functional Limitations

1. **No Real-Time Updates**: Manual page refresh required for new data
2. **No Multi-Language Support**: English only
3. **No Mobile Optimization**: Not responsive for mobile devices
4. **No Export to External Services**: Data export only to JSON
5. **No Collaboration Features**: Single-user application only
6. **No Data Import**: No way to import existing data
7. **No Automated Reminders**: No notification system

### Architectural Debt

1. **Alembic Not Used**: Database migrations not managed through Alembic
2. **No API Layer**: No REST API for external integrations
3. **Tight Coupling**: Business logic directly called from page controllers
4. **No Dependency Injection**: Components instantiated directly
5. **No Interface Definitions**: No abstract base classes or protocols

## References to Source Code

| Component           | Location                          | Key Classes/Functions                                |
| ------------------- | --------------------------------- | ---------------------------------------------------- |
| Application Entry   | `app.py`                          | `show_main_app()`, `show_home()`, `show_settings()`  |
| Authentication      | `login/auth.py`                   | `AuthManager`, `User` class                          |
| NLP Processing      | `models/nlp_processor.py`         | `NLPProcessor`, `analyze_entry()`                    |
| Pattern Detection   | `models/pattern_detector.py`      | `PatternDetector`, `detect_mood_trend()`             |
| Forecast Engine     | `models/forecast_engine.py`       | `ForecastEngine`, `generate_forecast()`              |
| Recommendations     | `models/recommendation_engine.py` | `RecommendationEngine`, `generate_recommendations()` |
| Visualizations      | `components/visualizations.py`    | `Visualizations`, `mood_trend_chart()`               |
| Database Operations | `utils/database.py`               | `get_entries()`, `save_entry()`, `get_user_stats()`  |
| Configuration       | `utils/config.py`                 | `validate_all_config()`, `get_secret_key()`          |
| Database Schema     | `utils/setup_postgres.sql`        | Table definitions, indexes, triggers                 |
