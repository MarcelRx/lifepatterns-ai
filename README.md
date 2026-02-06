# LifePatterns AI

**Personal Behavior & Outcome Analytics System**

A data-driven Streamlit application that analyzes daily user inputs (journal entries, activities, mood tracking) using Natural Language Processing and Machine Learning to identify behavioral patterns, predict life trajectory outcomes, and provide actionable improvement recommendations.

---

## Features

| Module | Description |
|--------|-------------|
| **Daily Input** | Journal entries with mood tracking, activity tags, and voice input |
| **Pattern Discovery** | AI-powered detection of emotional cycles, productivity waves, and habit streaks |
| **Outcome Forecast** | Predictive analytics showing life trajectory based on current patterns |
| **Smart Recommendations** | Personalized, actionable suggestions with projected impact |
| **Reports** | Day/Month/Year analytics with trend visualization |

---

## Tech Stack

- **Frontend:** Streamlit
- **LLM API:** Groq API (Llama3/Mixtral) - Ultra-fast inference
- **ML:** Scikit-learn, Pandas
- **Visualization:** Plotly
- **Database:** PostgreSQL
- **Language:** Python 3.9+

---

## Installation

```bash
# Clone repository
git clone https://github.com/MarcelRx/lifepatterns-ai.git 
cd lifepatterns-ai

# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL database
psql -U postgres -f setup_postgres.sql

# Configure environment
cp .env.example .env
# Edit .env with your Groq API key and database credentials

# Run application
streamlit run app.py
