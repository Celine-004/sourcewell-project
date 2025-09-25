"""
Modified Framingham Risk Score Calculator

10-year cardiovascular disease risk assessment with 2018 AHA/ACC modifications
and evidence-based treatment recommendations.
Based on: D'Agostino RB Sr, et al. Circulation. 2008;117(6):743-753.
"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class CVDRiskLevel(Enum):
    LOW = "low"
    BORDERLINE = "borderline"
    INTERMEDIATE = "intermediate" 
    HIGH = "high"

@dataclass
class FraminghamResult:
    """Framingham cardiovascular risk assessment results."""
    ten_year_risk_percentage: float
    risk_level: CVDRiskLevel
    risk_description: str
    bp_category: str
    recommendations: List[str]
    recommendation_citations: List[str]
    evidence_citations: List[str]
    supporting_evidence: List[Dict]

class ModifiedFraminghamCalculator:
    """Modified Framingham cardiovascular risk calculator with knowledge base integration."""
    
    # 2017 AHA/ACC Blood Pressure Categories
    BP_CATEGORIES = {
        'normal': {'systolic': (0, 119), 'diastolic': (0, 79), 'description': 'Normal'},
        'elevated': {'systolic': (120, 129), 'diastolic': (0, 79), 'description': 'Elevated'},
        'stage1': {'systolic': (130, 139), 'diastolic': (80, 89), 'description': 'Stage 1 Hypertension'},
        'stage2': {'systolic': (140, 180), 'diastolic': (90, 120), 'description': 'Stage 2 Hypertension'},
        'crisis': {'systolic': (180, 300), 'diastolic': (120, 200), 'description': 'Hypertensive Crisis'}
    }
    
    # Gender-specific Framingham coefficients (D'Agostino et al. 2008)
    COEFFICIENTS = {
        'male': {
            'age': 3.06117, 'total_cholesterol': 1.12370, 'hdl_cholesterol': -0.93263,
            'systolic_bp_treated': 1.93303, 'systolic_bp_untreated': 1.99881,
            'smoking': 0.65451, 'diabetes': 0.57367, 'constant': -23.9802,
            'baseline_survival': 0.88936
        },
        'female': {
            'age': 2.32888, 'total_cholesterol': 1.20904, 'hdl_cholesterol': -0.70833,
            'systolic_bp_treated': 2.76157, 'systolic_bp_untreated': 2.82263,
            'smoking': 0.52873, 'diabetes': 0.69154, 'constant': -26.1931,
            'baseline_survival': 0.95012
        }
    }
    
    def calculate_framingham_risk(self, patient_data: Dict[str, Any]) -> FraminghamResult:
        """Calculate 10-year CVD risk using Modified Framingham equation."""
        
        # Extract and validate required data
        age = patient_data.get('age')
        gender = patient_data.get('gender', '').lower()
        total_chol = patient_data.get('total_cholesterol')
        hdl_chol = patient_data.get('hdl_cholesterol')
        systolic_bp = patient_data.get('systolic_bp')
        diastolic_bp = patient_data.get('diastolic_bp')
        on_bp_meds = patient_data.get('on_bp_medication', False)
        smoking = patient_data.get('current_smoker', False)
        diabetes = patient_data.get('diabetes', False)
        
        # Framingham-specific validation
        if not (30 <= age <= 79):
            raise ValueError(f"Framingham equation validated for ages 30-79 years (patient age: {age})")
        if gender not in ['male', 'female']:
            raise ValueError("Gender must be 'male' or 'female'")
        
        required_fields = [total_chol, hdl_chol, systolic_bp]
        if any(x is None for x in required_fields):
            raise ValueError("Missing required fields: total cholesterol, HDL cholesterol, systolic BP")
        
        # Clinical validation ranges
        if not (100 <= total_chol <= 400):
            raise ValueError("Total cholesterol must be 100-400 mg/dL")
        if not (20 <= hdl_chol <= 100):
            raise ValueError("HDL cholesterol must be 20-100 mg/dL")
        if not (90 <= systolic_bp <= 200):
            raise ValueError("Systolic BP must be 90-200 mmHg")
        
        # Calculate risk score using validated coefficients
        coeff = self.COEFFICIENTS[gender]
        
        # Risk score components (natural logarithm transformation)
        age_score = math.log(age) * coeff['age']
        chol_score = math.log(total_chol) * coeff['total_cholesterol']
        hdl_score = math.log(hdl_chol) * coeff['hdl_cholesterol']
        
        # Blood pressure score (treatment-dependent)
        if on_bp_meds:
            bp_score = math.log(systolic_bp) * coeff['systolic_bp_treated']
        else:
            bp_score = math.log(systolic_bp) * coeff['systolic_bp_untreated']
        
        smoking_score = coeff['smoking'] if smoking else 0
        diabetes_score = coeff['diabetes'] if diabetes else 0
        
        # Calculate total risk score
        total_score = (age_score + chol_score + hdl_score + bp_score + 
                      smoking_score + diabetes_score + coeff['constant'])
        
        # Convert to 10-year risk percentage using gender-specific survival functions
        ten_year_risk = (1 - math.pow(coeff['baseline_survival'], math.exp(total_score))) * 100
        ten_year_risk = max(0, min(100, round(ten_year_risk, 1)))  # Clamp to 0-100%
        
        # Categorize risk and blood pressure
        risk_level, risk_description = self._categorize_cvd_risk(ten_year_risk)
        bp_category = self._categorize_blood_pressure(systolic_bp, diastolic_bp)
        
        # Generate evidence-based recommendations
        recommendations, rec_citations = self._generate_cvd_recommendations(
            ten_year_risk, bp_category, total_chol, hdl_chol, smoking, diabetes, on_bp_meds
        )
        
        # Retrieve supporting evidence
        general_citations, evidence = self._get_supporting_evidence()
        
        return FraminghamResult(
            ten_year_risk_percentage=ten_year_risk,
            risk_level=risk_level,
            risk_description=risk_description,
            bp_category=bp_category,
            recommendations=recommendations,
            recommendation_citations=rec_citations,
            evidence_citations=general_citations,
            supporting_evidence=evidence
        )
    
    def _categorize_cvd_risk(self, risk_percentage: float) -> Tuple[CVDRiskLevel, str]:
        """Categorize CVD risk using 2018 AHA/ACC guidelines."""
        if risk_percentage < 5.0:
            return CVDRiskLevel.LOW, "Low risk - continue preventive measures"
        elif risk_percentage < 7.5:
            return CVDRiskLevel.BORDERLINE, "Borderline risk - consider risk enhancers"
        elif risk_percentage < 20.0:
            return CVDRiskLevel.INTERMEDIATE, "Intermediate risk - lifestyle + possible medication"
        else:
            return CVDRiskLevel.HIGH, "High risk - intensive intervention recommended"
  
    def _categorize_blood_pressure(self, systolic: int, diastolic: int) -> str:
        """Categorize blood pressure using 2017 AHA/ACC guidelines - use highest category."""
        
        def categorize_systolic(sbp):
            if sbp >= 180: return 'crisis'
            elif sbp >= 140: return 'stage2'
            elif sbp >= 130: return 'stage1'
            elif sbp >= 120: return 'elevated'
            else: return 'normal'
        
        def categorize_diastolic(dbp):
            if dbp >= 120: return 'crisis'
            elif dbp >= 90: return 'stage2'
            elif dbp >= 80: return 'stage1'
            else: return 'normal'
        
        # Severity hierarchy for selecting highest category
        severity_order = {'normal': 0, 'elevated': 1, 'stage1': 2, 'stage2': 3, 'crisis': 4}
        
        sbp_category = categorize_systolic(systolic)
        dbp_category = categorize_diastolic(diastolic)
        
        # Use the higher severity category
        if severity_order[sbp_category] >= severity_order[dbp_category]:
            final_category = sbp_category
        else:
            final_category = dbp_category
        
        return self.BP_CATEGORIES[final_category]['description']
    
    def _generate_cvd_recommendations(self, ten_year_risk: float, bp_category: str,
                                    total_chol: int, hdl_chol: int, smoking: bool,
                                    diabetes: bool, on_bp_meds: bool) -> Tuple[List[str], List[str]]:
        """Generate evidence-based cardiovascular recommendations with guaranteed fallbacks."""
        recommendations = []
        citations = []
        
        try:
            from knowledge_base import MedicalSearchEngine
            
            with MedicalSearchEngine() as engine:
                # Statin therapy recommendations with guaranteed fallbacks
                statin_added = False
                if ten_year_risk >= 20.0:  # High risk
                    statin_results = engine.search_medical_content(
                        "high intensity statin therapy atorvastatin rosuvastatin AHA ACC", 
                        content_type="MedicalGuideline", limit=2
                    )
                    for result in statin_results:
                        if any(term in result.content.lower() for term in ['statin', 'atorvastatin', 'rosuvastatin']):
                            recommendations.append(
                                f"High-intensity statin therapy per {result.organization} guidelines (target LDL <70 mg/dL). Consult your medical provider."
                            )
                            citations.append(result.citation)
                            statin_added = True
                            break
                    
                    # Guaranteed fallback for high-risk statin therapy
                    if not statin_added:
                        recommendations.extend([
                            "High-intensity statin therapy (atorvastatin 40-80mg or rosuvastatin 20-40mg). Consult your medical provider.",
                            "Target LDL cholesterol <70 mg/dL"
                        ])
                        citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
                    
                elif ten_year_risk >= 7.5:  # Intermediate risk
                    statin_results = engine.search_medical_content(
                        "moderate intensity statin therapy cardiovascular prevention", 
                        content_type="MedicalGuideline", limit=2
                    )
                    for result in statin_results:
                        if 'statin' in result.content.lower():
                            recommendations.append(
                                f"Consider moderate-intensity statin therapy per {result.organization} guidelines. Consult your medical provider."
                            )
                            citations.append(result.citation)
                            statin_added = True
                            break
                    
                    # Guaranteed fallback for intermediate-risk statin therapy
                    if not statin_added:
                        recommendations.extend([
                            "Consider moderate-intensity statin therapy. Consult your medical provider.",
                            "Target LDL cholesterol <100 mg/dL"
                        ])
                        citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
                
                # Blood pressure management with guaranteed fallbacks
                if 'Hypertension' in bp_category:
                    bp_added = False
                    bp_results = engine.search_medical_content(
                        "hypertension treatment ACE inhibitor ARB target 130 80", 
                        content_type="MedicalGuideline", limit=2
                    )
                    for result in bp_results:
                        if any(term in result.content.lower() for term in ['ace inhibitor', 'arb', 'blood pressure']):
                            if not on_bp_meds:
                                recommendations.append("Initiate antihypertensive medication (ACE inhibitor or ARB preferred). Consult your medical provider.")
                            recommendations.append(f"Target blood pressure <130/80 mmHg per {result.organization} guidelines")
                            citations.append(result.citation)
                            bp_added = True
                            break
                    
                    if not bp_added:  # Guaranteed BP fallback
                        if not on_bp_meds:
                            recommendations.append("Initiate antihypertensive medication (ACE inhibitor or ARB preferred). Consult your medical provider.")
                        recommendations.append("Target blood pressure <130/80 mmHg")
                        citations.append("Whelton PK, et al. 2017 AHA/ACC High Blood Pressure Guideline. Circulation. 2018;138(17):e484-e594.")
                
                elif bp_category == 'Elevated':
                    recommendations.append("Intensive lifestyle modification for blood pressure control")
                    citations.append("Whelton PK, et al. 2017 AHA/ACC High Blood Pressure Guideline. Circulation. 2018;138(17):e484-e594.")
                
                # Critical smoking intervention with guaranteed fallbacks
                if smoking:
                    smoking_added = False
                    smoking_results = engine.search_medical_content(
                        "smoking cessation cardiovascular prevention nicotine replacement", 
                        content_type="MedicalGuideline", limit=2
                    )
                    for result in smoking_results:
                        if any(term in result.content.lower() for term in ['smoking', 'cessation', 'nicotine']):
                            recommendations.extend([
                                f"URGENT: Smoking cessation counseling per {result.organization} guidelines",
                                "Consider nicotine replacement therapy or varenicline. Consult your medical provider."
                            ])
                            citations.append(result.citation)
                            smoking_added = True
                            break
                    
                    if not smoking_added:  # Guaranteed smoking cessation fallback
                        recommendations.extend([
                            "URGENT: Smoking cessation counseling and pharmacotherapy",
                            "Consider nicotine replacement therapy or varenicline. Consult your medical provider."
                        ])
                        citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
                
                # Diabetes medications with CV benefit
                if diabetes:
                    diabetes_results = engine.search_medical_content(
                        "diabetes cardiovascular benefit SGLT2 GLP-1", 
                        content_type="MedicalGuideline", limit=2
                    )
                    diabetes_added = False
                    for result in diabetes_results:
                        if any(term in result.content.lower() for term in ['diabetes', 'sglt2', 'glp-1']):
                            recommendations.extend([
                                "Optimize diabetes control (HbA1c <7%)",
                                f"Consider SGLT2 inhibitor or GLP-1 RA for cardiovascular benefit. Consult your medical provider."
                            ])
                            citations.append(result.citation)
                            diabetes_added = True
                            break
                    
                    if not diabetes_added:  # Guaranteed diabetes fallback
                        recommendations.extend([
                            "Optimize diabetes control (HbA1c <7%)",
                            "Consider SGLT2 inhibitor or GLP-1 RA for cardiovascular benefit. Consult your medical provider."
                        ])
                        citations.append("American Diabetes Association. Standards of Medical Care in Diabetes-2024. Diabetes Care. 2024;47(Suppl 1):S1-S321.")
                
                # Universal lifestyle recommendations (always include)
                recommendations.extend([
                    "Mediterranean-style diet with reduced saturated fat",
                    "Regular aerobic exercise: 150 minutes/week moderate intensity"
                ])
                
                # Aspirin consideration for intermediate/high risk
                if ten_year_risk >= 7.5:
                    recommendations.append("Consider low-dose aspirin (81mg daily) if bleeding risk is low. Consult your medical provider.")
                    
        except Exception as e:
            print(f"Warning: Knowledge base unavailable ({e}), using complete evidence-based fallbacks")
            recommendations, citations = self._get_fallback_cvd_recommendations(
                ten_year_risk, bp_category, total_chol, hdl_chol, smoking, diabetes, on_bp_meds
            )
        
        # Remove duplicates while preserving order
        unique_recommendations = list(dict.fromkeys(recommendations))
        unique_citations = list(dict.fromkeys(citations))
        
        return unique_recommendations, unique_citations
    def _get_fallback_cvd_recommendations(self, ten_year_risk: float, bp_category: str,
                                        total_chol: int, hdl_chol: int, smoking: bool,
                                        diabetes: bool, on_bp_meds: bool) -> Tuple[List[str], List[str]]:
        """Evidence-based fallback recommendations with clinical disclaimers."""
        recommendations = []
        citations = []
        
        # Statin therapy recommendations
        if ten_year_risk >= 20.0:
            recommendations.extend([
                "High-intensity statin therapy (atorvastatin 40-80mg or rosuvastatin 20-40mg). Consult your medical provider.",
                "Target LDL cholesterol <70 mg/dL"
            ])
            citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
        elif ten_year_risk >= 7.5:
            recommendations.extend([
                "Consider moderate-intensity statin therapy. Consult your medical provider.",
                "Target LDL cholesterol <100 mg/dL"
            ])
            citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
        
        # Blood pressure management
        if 'Hypertension' in bp_category:
            if not on_bp_meds:
                recommendations.append("Initiate antihypertensive medication (ACE inhibitor or ARB preferred). Consult your medical provider.")
            recommendations.append("Target blood pressure <130/80 mmHg")
            citations.append("Whelton PK, et al. 2017 AHA/ACC High Blood Pressure Guideline. Circulation. 2018;138(17):e484-e594.")
        elif bp_category == 'Elevated':
            recommendations.append("Intensive lifestyle modification for blood pressure control")
            citations.append("Whelton PK, et al. 2017 AHA/ACC High Blood Pressure Guideline. Circulation. 2018;138(17):e484-e594.")
        
        # Critical interventions
        if smoking:
            recommendations.extend([
                "URGENT: Smoking cessation counseling and pharmacotherapy",
                "Consider nicotine replacement therapy or varenicline. Consult your medical provider."
            ])
            citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
        
        if diabetes:
            recommendations.extend([
                "Optimize diabetes control (HbA1c <7%)",
                "Consider SGLT2 inhibitor or GLP-1 RA for cardiovascular benefit. Consult your medical provider."
            ])
            citations.append("American Diabetes Association. Standards of Medical Care in Diabetes-2024. Diabetes Care. 2024;47(Suppl 1):S1-S321.")
        
        recommendations.extend([
            "Mediterranean-style diet with reduced saturated fat",
            "Regular aerobic exercise: 150 minutes/week moderate intensity"
        ])
        citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
        
        # Aspirin consideration
        if ten_year_risk >= 7.5:
            recommendations.append("Consider low-dose aspirin (81mg daily) if bleeding risk is low. Consult your medical provider.")
            citations.append("Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646.")
        
        return recommendations, citations
    
    def _get_supporting_evidence(self) -> Tuple[List[str], List[Dict]]:
        """Retrieve Framingham evidence from knowledge base."""
        citations = []
        evidence = []
        
        try:
            from knowledge_base import MedicalSearchEngine
            with MedicalSearchEngine() as engine:
                results = engine.search_by_calculator("ModifiedFramingham", limit=3)
                
                for result in results:
                    citations.append(result.citation)
                    evidence.append({
                        "title": result.title,
                        "organization": result.organization,
                        "journal": result.journal,
                        "year": result.publication_year,
                        "citation": result.citation,
                        "content_preview": result.content[:200] + "..." if len(result.content) > 200 else result.content
                    })
                    
        except Exception as e:
            # Fallback citations if KB unavailable
            citations = [
                "D'Agostino RB Sr, et al. General cardiovascular risk profile for use in primary care. Circulation. 2008;117(6):743-753.",
                "Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. Circulation. 2019;140(11):e596-e646."
            ]
            print(f"Warning: Knowledge base unavailable ({e}), using fallback citations")
            
        return citations, evidence

# Demo function
def demo_framingham():
    """Demonstrate Framingham calculator with test scenario."""
    try:
        from data_models.patient_data import PatientData, get_test_scenarios
        
        calculator = ModifiedFraminghamCalculator()
        scenarios = get_test_scenarios()
        patient = PatientData.from_dict(scenarios['high_risk_middle_aged_male'])
        
        # Validate patient data
        errors = patient.validate()
        if errors:
            print(" Patient validation failed:")
            for error in errors:
                print(f"   {error}")
            return
        
        # Calculate Framingham risk
        result = calculator.calculate_framingham_risk(patient.to_calculator_dict())
        
        print(" MODIFIED FRAMINGHAM CVD RISK ASSESSMENT")
        print("=" * 55)
        print(f"Patient: {patient.summary()}")
        print(f"10-Year CVD Risk: {result.ten_year_risk_percentage}%")
        print(f"Risk Level: {result.risk_level.value.upper()}")
        print(f"Blood Pressure: {result.bp_category}")
        print(f"Description: {result.risk_description}")
        
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec}")
        
        print(f"\nEvidence Citations: {len(result.evidence_citations)} sources")
        
    except ImportError as e:
        print(f" Import error: {e}")
    except Exception as e:
        print(f" Calculation error: {e}")

if __name__ == "__main__":
    demo_framingham()