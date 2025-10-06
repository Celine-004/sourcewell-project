"""
Risk Assessment Dashboard
Displays results from all three calculators
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import sys
from pathlib import Path

# Import existing calculator modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from calculators.runner import MultiCalculatorRunner

class RiskDashboard:
    """Risk assessment visualization and results"""
    
    def __init__(self):
        self.runner = MultiCalculatorRunner()
    
    def run_risk_assessment(self, patient_data) -> Dict[str, Any]:
        """Run all risk calculators"""
        try:
            # Run all calculators
            results = self.runner.run_all_assessments(patient_data)
            
            return results
            
        except Exception as e:
            st.error(f"Error running risk assessment: {e}")
            return {}
    
    def display_risk_summary(self, results: Dict[str, Any]):
        """Display risk assessment summary"""
        if not results or not results.get('success'):
            st.warning("No risk assessment results available")
            return
        
        st.subheader("🎯 Risk Assessment Results")
        
        # Get the actual calculator results
        calculator_results = results.get('results', {})
        
        if not calculator_results:
            st.warning("No calculator results available")
            return
        
        # Create columns for each calculator
        available_results = []
        for calc_name in ['diabetes', 'cardiovascular', 'colorectal_screening']:
            if calc_name in calculator_results:
                available_results.append(calc_name)
        
        if not available_results:
            st.warning("No calculator results available")
            return
        
        cols = st.columns(len(available_results))
        
        for i, calc_name in enumerate(available_results):
            calc_result = calculator_results[calc_name]
            
            with cols[i]:
                self._display_calculator_card(calc_name, calc_result)

    def _display_calculator_card(self, calc_name: str, result: Any):
        """Display individual calculator result card"""
        # Calculator titles and icons
        calc_info = {
            'diabetes': {
                'title': 'Diabetes Risk',
                'icon': '🍯',
                'description': 'FINDRISC 10-year T2D risk'
            },
            'cardiovascular': {
                'title': 'Cardiovascular Risk', 
                'icon': '❤️',
                'description': 'Modified Framingham CVD risk'
            },
            'colorectal_screening': {
                'title': 'Colorectal Screening',
                'icon': '🎗️',
                'description': 'CRC screening recommendations'
            }
        }
        
        info = calc_info.get(calc_name, {})
        
        # Create card
        with st.container():
            st.markdown(f"### {info.get('icon', '📊')} {info.get('title', calc_name.title())}")
            st.caption(info.get('description', ''))
            
            # Check if result is an error dictionary or an actual result object
            if isinstance(result, dict) and 'error' in result:
                self._display_error_result(result)
            else:
                # Result is a calculator result object (FINDRISCResult, FraminghamResult, etc.)
                self._display_successful_result(calc_name, result)

    def _display_successful_result(self, calc_name: str, result: Any):
        """Display successful calculator result"""   
        if calc_name == 'diabetes':
            self._display_findrisc_result(result)
        elif calc_name == 'cardiovascular':
            self._display_framingham_result(result)
        elif calc_name == 'colorectal_screening':
            self._display_colorectal_result(result)

    def _display_findrisc_result(self, data: Any):
        """Display FINDRISC results"""
        # Access attributes directly from the FINDRISCResult object
        score = data.total_score if hasattr(data, 'total_score') else 0
        
        # Handle risk_level which might be an enum
        if hasattr(data, 'risk_level'):
            if hasattr(data.risk_level, 'value'):
                risk_level = data.risk_level.value
            else:
                risk_level = str(data.risk_level)
        else:
            risk_level = 'unknown'
        
        ten_year_risk = data.ten_year_risk_percentage if hasattr(data, 'ten_year_risk_percentage') else 0
        
        # Risk level color coding
        risk_colors = {
            'low': 'green',
            'slightly_elevated': 'yellow',
            'moderate': 'orange', 
            'high': 'red',
            'very_high': 'darkred'
        }
        
        color = risk_colors.get(risk_level.lower(), 'gray')
        
        st.metric("FINDRISC Score", f"{score}/26")
        st.metric("Risk Level", risk_level.replace('_', ' ').title())
        st.metric("10-Year Risk", f"{ten_year_risk:.1f}%")
        
        # Progress bar for score
        progress = min(score / 26, 1.0)
        st.progress(progress)
        st.caption(f"Score: {score}/26")

    def _display_framingham_result(self, data: Any):
        """Display Framingham results"""
        # Access attributes directly from the FraminghamResult object
        ten_year_risk = data.ten_year_risk_percentage if hasattr(data, 'ten_year_risk_percentage') else 0
        bp_category = data.bp_category if hasattr(data, 'bp_category') else 'Unknown'
        risk_level_value = data.risk_level.value if hasattr(data, 'risk_level') else 'unknown'
        
        # Risk level based on percentage
        if ten_year_risk < 7.5:
            risk_level = "Low"
            color = "green"
        elif ten_year_risk < 20:
            risk_level = "Moderate" 
            color = "orange"
        else:
            risk_level = "High"
            color = "red"
        
        st.metric("10-Year CVD Risk", f"{ten_year_risk:.1f}%")
        st.metric("Risk Level", risk_level)
        st.metric("BP Category", bp_category)
        
        # Progress bar for risk
        progress = min(ten_year_risk / 30, 1.0)  # Cap at 30% for visualization
        st.progress(progress)
        st.caption(f"Risk: {ten_year_risk:.1f}%")

    def _display_colorectal_result(self, data: Any):
        """Display colorectal screening results"""
        # Access attributes directly from the ColorectalResult object
        recommendation = data.recommendation.value if hasattr(data, 'recommendation') else 'No recommendation'
        risk_level = data.risk_level if hasattr(data, 'risk_level') else 'Average'
        screening_interval = data.screening_interval if hasattr(data, 'screening_interval') else 'Not specified'
        
        # Simplify recommendation for display
        if 'start_now' in recommendation.lower():
            status = "✅ Screening Recommended"
            color = "green"
        elif 'discuss' in recommendation.lower():
            status = "⚠️ Consider Screening"
            color = "orange"
        else:
            status = "ℹ️ Follow Guidelines"
            color = "blue"
        
        st.metric("Risk Level", risk_level)
        st.markdown(f"**Status:** {status}")
        
        # Show recommendation details
        with st.expander("View Recommendation"):
            st.write(f"**Recommendation:** {recommendation.replace('_', ' ').title()}")
            st.write(f"**Screening Interval:** {screening_interval}")
            if hasattr(data, 'rationale'):
                st.write(f"**Rationale:** {data.rationale}")

    def _display_error_result(self, result: Dict[str, Any]):
        """Display error result"""
        error_msg = result.get('error', 'Unknown error occurred')
        st.error(f"Calculation failed: {error_msg}")
        
    def create_risk_visualization(self, results: Dict[str, Any]):
        """Create comprehensive risk visualization"""
        if not results or not results.get('success'):
            return
        
        st.subheader("📊 Risk Visualization")
        
        # Get the actual calculator results
        calculator_results = results.get('results', {})
        
        if not calculator_results:
            st.warning("No calculator results to visualize")
            return
        
        # Collect risk data
        risk_data = []
        
        # Process diabetes results
        if 'diabetes' in calculator_results:
            diabetes_result = calculator_results['diabetes']
            if not isinstance(diabetes_result, dict) or 'error' not in diabetes_result:
                if hasattr(diabetes_result, 'ten_year_risk_percentage'):
                    risk_data.append({
                        'Calculator': 'Diabetes (FINDRISC)',
                        '10-Year Risk %': diabetes_result.ten_year_risk_percentage,
                        'Category': 'Metabolic'
                    })
        
        # Process cardiovascular results
        if 'cardiovascular' in calculator_results:
            cvd_result = calculator_results['cardiovascular']
            if not isinstance(cvd_result, dict) or 'error' not in cvd_result:
                if hasattr(cvd_result, 'ten_year_risk_percentage'):
                    risk_data.append({
                        'Calculator': 'Cardiovascular (Framingham)',
                        '10-Year Risk %': cvd_result.ten_year_risk_percentage,
                        'Category': 'Cardiovascular'
                    })
        
        if risk_data:
            # Create bar chart
            fig = px.bar(
                risk_data,
                x='Calculator',
                y='10-Year Risk %',
                color='Category',
                title='10-Year Risk Assessment Comparison',
                color_discrete_map={
                    'Metabolic': '#FF6B6B',
                    'Cardiovascular': '#4ECDC4'
                }
            )
            
            fig.update_layout(
                xaxis_title="Risk Calculator",
                yaxis_title="10-Year Risk Percentage",
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a combined risk gauge
            if len(risk_data) > 0:
                col1, col2 = st.columns(2)
                
                for i, data in enumerate(risk_data):
                    with col1 if i == 0 else col2:
                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=data['10-Year Risk %'],
                            title={'text': data['Calculator']},
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={
                                'axis': {'range': [None, 50]},
                                'bar': {'color': "darkred" if data['10-Year Risk %'] > 20 else "orange" if data['10-Year Risk %'] > 10 else "green"},
                                'steps': [
                                    {'range': [0, 10], 'color': "lightgreen"},
                                    {'range': [10, 20], 'color': "yellow"},
                                    {'range': [20, 30], 'color': "orange"},
                                    {'range': [30, 50], 'color': "lightcoral"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': data['10-Year Risk %']
                                }
                            }
                        ))
                        fig_gauge.update_layout(height=250)
                        st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("No risk percentages available for visualization")
        
        # Risk factors summary
        self._display_risk_factors_summary(calculator_results)

    def _display_risk_factors_summary(self, calculator_results: Dict[str, Any]):
        """Display summary of identified risk factors"""
        st.subheader("⚠️ Identified Risk Factors")
        
        risk_factors = []
        priority_actions = []
        
        # Process each calculator's results
        for calc_name in ['diabetes', 'cardiovascular', 'colorectal_screening']:
            if calc_name not in calculator_results:
                continue
                
            calc_result = calculator_results[calc_name]
            
            # Skip if there was an error
            if isinstance(calc_result, dict) and 'error' in calc_result:
                continue
            
            # Extract recommendations (they're attributes of the result objects)
            if hasattr(calc_result, 'recommendations'):
                for rec in calc_result.recommendations:
                    if isinstance(rec, str):
                        if 'URGENT' in rec.upper() or 'CRITICAL' in rec.upper():
                            priority_actions.append(f"🔴 {rec}")
                        elif 'risk' in rec.lower():
                            risk_factors.append(rec)
            
            # Add specific risk factors based on values
            if calc_name == 'diabetes' and hasattr(calc_result, 'risk_level'):
                if calc_result.risk_level.value in ['high', 'very_high']:
                    risk_factors.append("High diabetes risk identified")
            
            if calc_name == 'cardiovascular' and hasattr(calc_result, 'ten_year_risk_percentage'):
                if calc_result.ten_year_risk_percentage >= 20:
                    risk_factors.append("High cardiovascular risk (≥20%)")
                elif calc_result.ten_year_risk_percentage >= 10:
                    risk_factors.append("Moderate cardiovascular risk (10-20%)")
        
        # Display priority actions
        if priority_actions:
            st.markdown("**🚨 Priority Actions:**")
            for action in priority_actions[:5]:  # Show top 5
                st.markdown(f"- {action}")
        
        # Display risk factors
        if risk_factors:
            st.markdown("**📋 Risk Factors Identified:**")
            # Remove duplicates and show
            unique_factors = list(dict.fromkeys(risk_factors))
            for factor in unique_factors[:5]:  # Show top 5
                st.markdown(f"- {factor}")
        
        if not risk_factors and not priority_actions:
            st.success("✅ No major risk factors identified based on current data")