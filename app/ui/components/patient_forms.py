"""
Patient Data Collection Forms
Integrates with existing PatientData class
"""
import streamlit as st
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Import existing patient data class
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data_models.patient_data import PatientData

class PatientDataCollector:
    """Handles patient data collection with validation"""
    
    def __init__(self):
        self.patient_data = None
    
    def collect_basic_info(self) -> Dict[str, Any]:
        """Collect Tier 1 basic information"""
        st.subheader("📋 Basic Information")

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input(
                "Age (years)",
                min_value=18,
                max_value=100,
                value=self._get_saved('age', 45),
                help="Age must be between 18-100 years"
            )

            gender = st.selectbox(
                "Biological Sex",
                options=["male", "female"],
                index=["male", "female"].index(self._get_saved('gender', 'male')),
                help="Required for risk calculations"
            )

            height_cm = st.number_input(
                "Height (cm)",
                min_value=100.0,
                max_value=250.0,
                value=float(self._get_saved('height_cm', 170.0)),
                step=0.1
            )

        with col2:
            weight_kg = st.number_input(
                "Weight (kg)",
                min_value=30.0,
                max_value=300.0,
                value=float(self._get_saved('weight_kg', 70.0)),
                step=0.1
            )

            physical_activity = st.checkbox(
                "Regular Physical Activity",
                value=self._get_saved('physical_activity', True),
                help="At least 150 minutes moderate activity per week"
            )

            vegetable_fruit_daily = st.checkbox(
                "Daily Fruits & Vegetables",
                value=self._get_saved('vegetable_fruit_daily', True),
                help="5+ servings per day"
            )

        return {
            "age": age,
            "gender": gender,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "physical_activity": physical_activity,
            "vegetable_fruit_daily": vegetable_fruit_daily
        }
    
    def _get_saved(self, key, default=None):
        """Get previously saved value from form_data"""
        form_data = st.session_state.get('form_data', {})
        return form_data.get(key, default)


    def collect_clinical_data(self) -> Dict[str, Any]:
        """Collect Tier 2 clinical measurements"""
        st.subheader("🩺 Clinical Measurements")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Blood Pressure**")
            systolic_bp = st.number_input(
                "Systolic (mmHg)",
                min_value=70,
                max_value=250,
                value=self._get_saved('systolic_bp', 120),
                help="Top number in blood pressure reading"
            )

            diastolic_bp = st.number_input(
                "Diastolic (mmHg)",
                min_value=40,
                max_value=150,
                value=self._get_saved('diastolic_bp', 80),
                help="Bottom number in blood pressure reading"
            )

            waist_circumference = st.number_input(
                "Waist Circumference (cm)",
                min_value=40,
                max_value=200,
                value=self._get_saved('waist_circumference', 85),
                help="Measured at narrowest point"
            )

        with col2:
            st.markdown("**Cholesterol Levels**")
            total_cholesterol = st.number_input(
                "Total Cholesterol (mg/dL)",
                min_value=100,
                max_value=500,
                value=self._get_saved('total_cholesterol', 200),
                help="From recent blood test"
            )

            hdl_cholesterol = st.number_input(
                "HDL Cholesterol (mg/dL)",
                min_value=15,
                max_value=100,
                value=self._get_saved('hdl_cholesterol', 50),
                help="'Good' cholesterol level"
            )

        return {
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "waist_circumference": waist_circumference,
            "total_cholesterol": total_cholesterol,
            "hdl_cholesterol": hdl_cholesterol
        }

    
    def collect_medical_history(self) -> Dict[str, Any]:
        """Collect Tier 3 medical and family history"""
        st.subheader("🧬 Medical & Family History")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Personal Medical History**")
            diabetes_diagnosed = st.checkbox("Diagnosed with Diabetes", value=self._get_saved('diabetes_diagnosed', False))
            high_glucose_history = st.checkbox("Previous High Blood Sugar", value=self._get_saved('high_glucose_history', False))
            hypertension_medication = st.checkbox("Blood Pressure Medication", value=self._get_saved('hypertension_medication', False))
            current_smoker = st.checkbox("Current Smoker", value=self._get_saved('current_smoker', False))

            st.markdown("**Cancer Screening History**")
            personal_history_polyps = st.checkbox("History of Polyps", value=self._get_saved('personal_history_polyps', False))
            inflammatory_bowel_disease = st.checkbox("Inflammatory Bowel Disease", value=self._get_saved('inflammatory_bowel_disease', False))
            high_risk_syndrome = st.checkbox("High Risk Genetic Syndrome", value=self._get_saved('high_risk_syndrome', False))

        with col2:
            st.markdown("**Family History**")

            diabetes_options = ["none", "grandparent_aunt_uncle_cousin", "parent_sibling_child"]
            saved_diabetes = self._get_saved('family_diabetes_history', 'none')
            family_diabetes_history = st.selectbox(
                "Family Diabetes History",
                options=diabetes_options,
                index=diabetes_options.index(saved_diabetes) if saved_diabetes in diabetes_options else 0,
                format_func=lambda x: {
                    "none": "No Family History",
                    "grandparent_aunt_uncle_cousin": "Grandparent/Aunt/Uncle/Cousin",
                    "parent_sibling_child": "Parent/Sibling/Child"
                }[x]
            )

            family_colorectal_cancer = st.checkbox("Family Colorectal Cancer", value=self._get_saved('family_colorectal_cancer', False))

            family_colorectal_age = None
            if family_colorectal_cancer:
                family_colorectal_age = st.number_input(
                    "Age at Family Member's Diagnosis",
                    min_value=20,
                    max_value=100,
                    value=self._get_saved('family_colorectal_age', 60)
                )

        return {
            "diabetes_diagnosed": diabetes_diagnosed,
            "high_glucose_history": high_glucose_history,
            "hypertension_medication": hypertension_medication,
            "current_smoker": current_smoker,
            "personal_history_polyps": personal_history_polyps,
            "inflammatory_bowel_disease": inflammatory_bowel_disease,
            "high_risk_syndrome": high_risk_syndrome,
            "family_diabetes_history": family_diabetes_history,
            "family_colorectal_cancer": family_colorectal_cancer,
            "family_colorectal_age": family_colorectal_age
        }

    
    def validate_and_create_patient_data(self, data: Dict[str, Any]) -> Optional[PatientData]:
        """Validate collected data and create PatientData instance"""
        try:
            patient = PatientData.from_dict(data)
            validation_errors = patient.validate()
            
            if validation_errors:
                st.error("Please fix the following errors:")
                for error in validation_errors:
                    st.error(f"• {error}")
                return None
            
            return patient
            
        except Exception as e:
            st.error(f"Error creating patient data: {e}")
            return None
    
    def display_patient_summary(self, patient_data: PatientData):
        """Display patient data summary"""
        st.subheader("📊 Patient Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Age", f"{patient_data.age} years")
            st.metric("Gender", patient_data.gender.title())
            st.metric("BMI", f"{patient_data.bmi:.1f}" if patient_data.bmi else "N/A")
        
        with col2:
            if patient_data.systolic_bp and patient_data.diastolic_bp:
                st.metric("Blood Pressure", f"{patient_data.systolic_bp}/{patient_data.diastolic_bp}")
            if patient_data.total_cholesterol:
                st.metric("Total Cholesterol", f"{patient_data.total_cholesterol} mg/dL")
        
        with col3:
            st.write("**Risk Factors:**")
            risk_summary = patient_data.clinical_summary()
            st.write(risk_summary)