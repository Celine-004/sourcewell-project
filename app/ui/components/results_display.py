"""
Results Display 
"""
import streamlit as st
from typing import Dict, Any, Optional, List

class ResultsDisplay:
    """Component for displaying risk assessment results"""
    
    def __init__(self):
        """Initialize the results display component"""
        pass
    
    def render(self, results: Optional[Dict[str, Any]] = None):
        """Render the results display"""
        if not results:
            st.info("No results to display yet. Complete an assessment first.")
            return
        
        if not results.get('success'):
            st.error("Assessment failed. Please check your data and try again.")
            return
        
        # Display summary
        st.subheader("📊 Assessment Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Calculators Run",
                results.get('calculators_run', 0),
                f"{results.get('successful_assessments', 0)} successful"
            )
        
        with col2:
            st.metric(
                "Assessment Date",
                results.get('assessment_date', 'Unknown')[:10]
            )
        
        with col3:
            priority_count = len(results.get('priority_actions', []))
            st.metric(
                "Priority Actions",
                priority_count,
                "Urgent" if priority_count > 0 else "None"
            )
        
        # Display results
        if results.get('results'):
            st.subheader("🎯 Risk Assessment Results")
            
            calc_results = results['results']
            
            # Diabetes results
            if 'diabetes' in calc_results:
                self._display_diabetes_result(calc_results['diabetes'])
            
            # Cardiovascular results
            if 'cardiovascular' in calc_results:
                self._display_cardiovascular_result(calc_results['cardiovascular'])
            
            # Colorectal results
            if 'colorectal_screening' in calc_results:
                self._display_colorectal_result(calc_results['colorectal_screening'])
        
        # Priority actions
        if results.get('priority_actions'):
            st.subheader("⚠️ Priority Actions")
            for action in results['priority_actions']:
                st.warning(action)
    
    def _display_diabetes_result(self, result):
        """Display diabetes risk result"""
        if isinstance(result, dict) and 'error' in result:
            st.error(f"Diabetes assessment failed: {result['error']}")
        elif hasattr(result, 'total_score'):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("FINDRISC Score", f"{result.total_score}/26")
            with col2:
                st.metric("10-Year Risk", f"{result.ten_year_risk_percentage}%")
    
    def _display_cardiovascular_result(self, result):
        """Display cardiovascular risk result"""
        if isinstance(result, dict) and 'error' in result:
            st.error(f"Cardiovascular assessment failed: {result['error']}")
        elif hasattr(result, 'ten_year_risk_percentage'):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("10-Year CVD Risk", f"{result.ten_year_risk_percentage}%")
            with col2:
                st.metric("BP Category", result.bp_category)
    
    def _display_colorectal_result(self, result):
        """Display colorectal screening result"""
        if isinstance(result, dict) and 'error' in result:
            st.error(f"Colorectal assessment failed: {result['error']}")
        elif hasattr(result, 'recommendation'):
            st.info(f"Screening: {result.recommendation.value.replace('_', ' ').title()}")