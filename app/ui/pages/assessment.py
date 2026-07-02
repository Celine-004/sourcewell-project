"""
Assessment Page - Risk Calculator Execution
"""
import streamlit as st
from typing import Dict, Any
import sys
from pathlib import Path

def render(interface):
    """Render the Assessment page"""
    st.title("🎯 Assessment - Risk Calculation")
    st.markdown("*Run evidence-based risk assessments*")
    
    # Progress indicator
    st.progress(0.50)
    st.caption("Step 2 of 4: Risk Assessment")
    
    # Check if patient data exists
    if not st.session_state.get('patient_data'):
        st.warning("⚠️ No patient data available. Please complete the Patient History section first.")
        if st.button("Go to Patient History"):
            st.rerun()
        return
    
    patient_data = st.session_state.patient_data
    
    # Display patient summary
    st.subheader("👤 Patient Overview")
    with st.expander("View Patient Summary"):
        interface.patient_data_collector.display_patient_summary(patient_data)
    
    # Risk assessment section
    st.subheader("🧮 Risk Calculators")
    
    # Calculator selection (for demo - normally would run all)
    st.markdown("**Available Risk Assessments:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        run_findrisc = st.checkbox("🍯 Diabetes Risk (FINDRISC)", value=True)
        st.caption("10-year Type 2 Diabetes risk")
    
    with col2:
        run_framingham = st.checkbox("❤️ Cardiovascular Risk", value=True)
        st.caption("10-year CVD risk (Modified Framingham)")
    
    with col3:
        run_colorectal = st.checkbox("🎗️ Colorectal Screening", value=True)
        st.caption("Cancer screening recommendations")
    
    st.markdown("---")
    
    # Run assessment button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🚀 Run Risk Assessment", type="primary", use_container_width=True):
            with st.spinner("Running risk calculations..."):
                # Run risk assessment
                results = interface.risk_dashboard.run_risk_assessment(patient_data)
                
                if results:
                    st.session_state.risk_results = results
                                        # Save to database
                    if 'db' in st.session_state and 'session_id' in st.session_state:
                        try:
                            st.session_state.db.save_risk_results(
                                st.session_state.session_id, results
                            )
                        except Exception:
                            pass  # Risk results may not be fully serializable

                    st.success("✅ Risk assessment completed!")
                else:
                    st.error("❌ Failed to run risk assessment")
    
    # Display results if available
    if st.session_state.get('risk_results'):
        st.markdown("---")
        
        # Display risk summary
        interface.risk_dashboard.display_risk_summary(st.session_state.risk_results)
        
        # Display visualization
        interface.risk_dashboard.create_risk_visualization(st.session_state.risk_results)
        
        # Navigation hint
        st.info("Navigate to 'Report' to get AI explanations and recommendations")
    
    # Debug information (can be removed in production)
    if st.checkbox("🐛 Show Debug Info"):
        st.json({
            "patient_data_available": bool(st.session_state.get('patient_data')),
            "risk_results_available": bool(st.session_state.get('risk_results')),
            "session_keys": list(st.session_state.keys())
        })