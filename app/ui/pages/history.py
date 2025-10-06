"""
Patient History Page - Data Collection
"""
import streamlit as st
from typing import Dict, Any
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def render(interface):
    """Render the Patient History page"""
    st.title("🧬 Patient History - Health Information")
    st.markdown("*Collect your personal and family health information*")
    
    # Progress indicator
    st.progress(0.25)
    st.caption("Step 1 of 4: Data Collection")
    
    # Create tabs for different data tiers
    tab1, tab2, tab3 = st.tabs(["📋 Basic Info", "🩺 Clinical Data", "🧬 Medical History"])
    
    # Initialize session state for form data
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    with tab1:
        st.markdown("### Basic Demographics & Lifestyle")
        basic_data = interface.patient_data_collector.collect_basic_info()
        st.session_state.form_data.update(basic_data)
    
    with tab2:
        st.markdown("### Clinical Measurements")
        st.info("💡 These measurements help provide more accurate risk assessments")
        clinical_data = interface.patient_data_collector.collect_clinical_data()
        st.session_state.form_data.update(clinical_data)
    
    with tab3:
        st.markdown("### Personal & Family Medical History")
        st.info("🔒 All information is processed locally and never shared")
        history_data = interface.patient_data_collector.collect_medical_history()
        st.session_state.form_data.update(history_data)
    
    # Validation and navigation
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔍 Validate & Continue", type="primary", use_container_width=True):
            # Validate data
            patient_data = interface.patient_data_collector.validate_and_create_patient_data(
                st.session_state.form_data
            )
            
            if patient_data:
                # Store in session state
                st.session_state.patient_data = patient_data
                st.success("✅ Data validated successfully!")
                
                # Show summary
                interface.patient_data_collector.display_patient_summary(patient_data)
                
                # Navigation hint
                st.info("👉 Navigate to 'Assessment' to run your risk calculations")
            else:
                st.error("❌ Please correct the validation errors above")
    
    # Show current patient summary if available
    if st.session_state.get('patient_data'):
        with st.expander("📊 Current Patient Summary"):
            interface.patient_data_collector.display_patient_summary(
                st.session_state.patient_data
            )