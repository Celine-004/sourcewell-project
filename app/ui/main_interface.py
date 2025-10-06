"""
Main Streamlit Interface
"""
import streamlit as st
from typing import Dict, Any, Optional
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from calculators.runner import MultiCalculatorRunner
from knowledge_base.search_engine import MedicalSearchEngine
from data_models.patient_data import PatientData

from .components.patient_forms import PatientDataCollector
from .components.risk_dashboard import RiskDashboard
from .components.results_display import ResultsDisplay
from .components.citation_viewer import CitationViewer
from .pages import history, assessment, report, coaching

class SourceWellInterface:
    """Main interface orchestrating all components"""
    
    def __init__(self):
        self.patient_data_collector = PatientDataCollector()
        self.risk_dashboard = RiskDashboard()
        self.results_display = ResultsDisplay()
        self.citation_viewer = CitationViewer()
        self.initialize_session_state()
        
        # Initialize session state
        if 'patient_data' not in st.session_state:
            st.session_state.patient_data = None
        if 'risk_results' not in st.session_state:
            st.session_state.risk_results = None
        if 'ai_explanations' not in st.session_state:
            st.session_state.ai_explanations = None
        
    def initialize_session_state(self):
        """Initialize session state with proper defaults"""
        if 'patient_data' not in st.session_state:
            st.session_state.patient_data = None
        if 'risk_results' not in st.session_state:
            st.session_state.risk_results = None
        if 'ai_explanations' not in st.session_state:
            st.session_state.ai_explanations = None
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {}
        if 'ai_engine' not in st.session_state:
            st.session_state.ai_engine = None

    def run(self):
        """Main application flow"""
        self.load_custom_styles()
        
        page = self.create_sidebar()
        
        # Route to appropriate page
        if page == "Patient History":
            history.render(self)
        elif page == "Assessment":
            assessment.render(self)
        elif page == "Report":
            report.render(self)
        elif page == "Coaching":
            coaching.render(self)
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        st.sidebar.title("🏥 SourceWell")
        st.sidebar.markdown("Evidence-Based Health Guidance")
        
        pages = ["Patient History", "Assessment", "Report", "Coaching"]
        return st.sidebar.radio("Navigate", pages)
    
    def load_custom_styles(self):
        """Load custom CSS styling"""
        css_file = Path(__file__).parent / "styles" / "custom.css"
        if css_file.exists():
            with open(css_file) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)