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
    
    # Set environment variables from config
    cache_paths = config.get('cache_paths', {})
    os.environ['HF_HOME'] = cache_paths.get('huggingface')
    os.environ['TEMP'] = cache_paths.get('temp')
    os.environ['TMP'] = cache_paths.get('temp')
    os.environ['PIP_CACHE_DIR'] = cache_paths.get('pip_cache')

import streamlit as st
sys.path.insert(0, str(project_root))

from calculators import runner as calculator_runner
from knowledge_base import search_engine
from app.ui.main_interface import SourceWellInterface

def main():
    """Main application entry point"""
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