"""
SourceWell Platform - Main Streamlit Application
"""
import os
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
config_file = project_root / "sourcewell_config.json"

if config_file.exists():
    with open(config_file, 'r') as f:
        config = json.load(f)

    cache_paths = config.get('cache_paths', {})
    os.environ['HF_HOME'] = cache_paths.get('huggingface', '')
    os.environ['TEMP'] = cache_paths.get('temp', '')
    os.environ['TMP'] = cache_paths.get('temp', '')
    os.environ['PIP_CACHE_DIR'] = cache_paths.get('pip_cache', '')

import streamlit as st
sys.path.insert(0, str(project_root))

from app.data.database import UserDatabase
from app.ui.main_interface import SourceWellInterface


def show_login():
    """Show login/register screen"""
    st.set_page_config(
        page_title="SourceWell Healthcare Platform",
        page_icon="🏥",
        layout="centered"
    )

    st.title("🏥 SourceWell")
    st.markdown("Evidence-Based Health Guidance")
    st.markdown("---")

    db = UserDatabase()

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                user_id = db.authenticate(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.session_state.db = db

                    # Check for previous sessions
                    previous = db.get_user_sessions(user_id)
                    if previous and previous[0].get('patient_data'):
                        st.session_state.pending_login = True
                        st.session_state.previous_sessions = previous
                    else:
                        st.session_state.session_id = db.create_session(user_id)
                    st.rerun()

                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")

    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register", use_container_width=True):
            if not new_user or not new_pass:
                st.warning("Please fill in all fields")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            elif len(new_pass) < 6:
                st.error("Password must be at least 6 characters")
            elif db.create_user(new_user, new_pass):
                st.success("Account created. Please login.")
            else:
                st.error("Username already exists")

def show_session_picker():
    """Let user choose to continue previous session or start new"""
    st.set_page_config(
        page_title="SourceWell Healthcare Platform",
        page_icon="🏥",
        layout="centered"
    )

    db = st.session_state.db
    st.title("🏥 Welcome back, " + st.session_state.username)
    st.markdown("---")

    sessions = st.session_state.previous_sessions

    if st.button("🆕 Start New Session", type="primary", use_container_width=True):
        session_id = db.create_session(st.session_state.user_id)
        st.session_state.session_id = session_id
        del st.session_state['pending_login']
        del st.session_state['previous_sessions']
        st.rerun()

    st.markdown("**Or continue a previous session:**")

    for session in sessions[:5]:
        label = f"Session from {session['created_at']}"
        if session.get('patient_data'):
            pd = session['patient_data']
            label += f" — {pd.get('age', '?')}y/o {pd.get('gender', '?')}"

        if st.button(label, key=f"session_{session['id']}", use_container_width=True):
            st.session_state.session_id = session['id']

            # Load chat history
            history = db.get_chat_history(session['id'])
            st.session_state.coaching_chat = [
                {"role": h["role"], "content": h["content"]} for h in history
            ]

            # Load patient data into form for re-validation
            if session.get('patient_data'):
                saved = session['patient_data']
                # Remap calculator keys back to form field names
                key_map = {
                    'diabetes': 'diabetes_diagnosed',
                    'family_history_first_degree': 'family_colorectal_cancer',
                    'family_history_age': 'family_colorectal_age',
                }
                for old_key, new_key in key_map.items():
                    if old_key in saved and new_key not in saved:
                        saved[new_key] = saved[old_key]
                st.session_state.form_data = saved


            del st.session_state['pending_login']
            del st.session_state['previous_sessions']
            st.rerun()

def main():
    """Main application entry point"""
    if 'user_id' not in st.session_state:
        show_login()
        return
        
    if st.session_state.get('pending_login'):
        show_session_picker()
        return
        
    st.set_page_config(
        page_title="SourceWell Healthcare Platform",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    interface = SourceWellInterface()
    interface.run()


if __name__ == "__main__":
    main()
