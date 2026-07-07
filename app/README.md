# SourceWell App Module

Streamlit web interface with user authentication, session persistence, multi-page health assessment workflow, and AI coaching chat.

## Overview

The app module provides the primary user interface for SourceWell. It handles user registration and login, persistent sessions backed by SQLite, patient data collection with saved-session pre-filling, risk calculator execution and visualization, AI-generated explanations with citation verification, and an AI coaching chat for follow-up health questions.

## Architecture

```
app/ 
├── main.py             # Entry point: login, session picker, app launch 
├── data/ 
│ ├── database.py       # SQLite user/session/chat persistence 
│ └── init.py 
└── ui/ 
├── main_interface.py   # Page navigation and session state orchestration 
├── styles/ 
│ └── custom.css        # Custom Streamlit styling ├── pages/ 
│ ├── history.py        # Patient data collection (3-tier forms) 
│ ├── assessment.py     # Risk calculator execution 
│ ├── report.py         # AI explanations with citations and verification 
│ └── coaching.py       # Health recommendations + AI chat 
└── components/ 
├── patient_forms.py    # Form widgets with session pre-fill (_get_saved) 
├── risk_dashboard.py   # Plotly risk visualization (bar, gauge, cards) 
├── results_display.py  # Risk results presentation 
└── citation_viewer.py  # Medical citation display
```


## User Flow

The application presents a login or registration screen on first visit. Returning users can select a previous session to restore patient data, risk results, and chat history, or start a new session. The workflow then proceeds through four pages: Patient History (data collection across basic info, clinical measurements, and medical/family history), Assessment (FINDRISC, Framingham, and Colorectal risk calculators with visual results), Report (AI-generated explanations with optional citation verification and detailed analysis), and Coaching (static health recommendations with an AI chat for personalized follow-up questions).

## Session Persistence

The `app/data/database.py` module manages a SQLite database stored at `.db/sourcewell.db` (excluded from git). It tracks user accounts, sessions with timestamps, patient data snapshots, and chat history. When a user loads a previous session, form fields are pre-filled via the `_get_saved` helper in `patient_forms.py`, with key remapping to handle differences between calculator output keys and form field names.

## Running the Application

```bash
# Ensure Weaviate is running
docker compose up -d

# Launch
streamlit run app/main.py
```

The application is accessible at http://localhost:8501.

## Dependencies

The app module depends on the calculators, knowledge_base, data_models, and llm modules internally. External dependencies include Streamlit, Plotly, and the standard library. The SQLite database requires no additional installation.
