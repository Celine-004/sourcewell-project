"""
FINDRISC (Finnish Diabetes Risk Score) Calculator

Validated 10-year Type 2 diabetes risk assessment with evidence-based recommendations.
Based on: Lindström J, Tuomilehto J. Diabetes Care. 2003;26(3):725-731.
"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class DiabetesRiskLevel(Enum):
    LOW = "low"
    SLIGHTLY_ELEVATED = "slightly_elevated"
    MODERATE = "moderate" 
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class FINDRISCResult:
    """FINDRISC assessment results with evidence-based recommendations."""
    total_score: int
    risk_level: DiabetesRiskLevel
    ten_year_risk_percentage: float
    risk_description: str
    recommendations: List[str]
    recommendation_citations: List[str]  # Citations for recommendations
    evidence_citations: List[str]        # General FINDRISC evidence
    supporting_evidence: List[Dict]

class FINDRISCCalculator:
    """FINDRISC diabetes risk calculator with knowledge base integration."""
    
    # Validated FINDRISC risk categories (score_range: (risk_level, 10_year_risk_%, description))
    RISK_CATEGORIES = {
        (0, 7): (DiabetesRiskLevel.LOW, 1.0, "Low risk - maintain healthy lifestyle"),
        (8, 11): (DiabetesRiskLevel.SLIGHTLY_ELEVATED, 4.0, "Slightly elevated - monitor lifestyle"),
        (12, 14): (DiabetesRiskLevel.MODERATE, 17.0, "Moderate risk - lifestyle intervention recommended"),
        (15, 20): (DiabetesRiskLevel.HIGH, 33.0, "High risk - medical evaluation needed"),
        (21, 26): (DiabetesRiskLevel.VERY_HIGH, 50.0, "Very high risk - immediate medical attention")
    }
    
    def calculate_findrisc(self, patient_data: Dict[str, Any]) -> FINDRISCResult:       
        age = patient_data.get('age')
        bmi = patient_data.get('bmi')
        waist = patient_data.get('waist_circumference')
        gender = patient_data.get('gender', '').lower()
        
        if any(x is None for x in [age, bmi, waist, gender]):
            raise ValueError("Missing required fields for FINDRISC calculation")
        
        if bmi is None:
            raise ValueError("BMI is required (auto-calculated from height/weight)")
        
        total_score = 0
        
        # Age scoring (0-4 points)
        if 45 <= age <= 54: total_score += 2
        elif 55 <= age <= 64: total_score += 3
        elif age >= 65: total_score += 4
        
        # BMI scoring (0-3 points)
        if 25 <= bmi < 30: total_score += 1
        elif bmi >= 30: total_score += 3
        
        # Waist circumference scoring (gender-specific, 0-4 points)
        if gender == 'male':
            if 94 <= waist <= 101: total_score += 3
            elif waist >= 102: total_score += 4
        else:  # female
            if 80 <= waist <= 87: total_score += 3
            elif waist >= 88: total_score += 4
        
        # Lifestyle and medical history scoring
        if not patient_data.get('physical_activity', True): total_score += 2
        if not patient_data.get('vegetable_fruit_daily', True): total_score += 1
        if patient_data.get('hypertension_medication', False): total_score += 2
        if patient_data.get('high_glucose_history', False): total_score += 5
        
        # Family history scoring (0-5 points)
        family_history = patient_data.get('family_diabetes_history', 'none')
        if family_history == 'grandparent_aunt_uncle_cousin': total_score += 3
        elif family_history == 'parent_sibling_child': total_score += 5
        
        # Determine risk category and generate results
        risk_level, risk_percentage, description = self._get_risk_category(total_score)
        recommendations, rec_citations = self._generate_recommendations(total_score, bmi, patient_data)
        
        # Get general FINDRISC evidence
        general_citations, evidence = self._get_supporting_evidence()
        
        return FINDRISCResult(
            total_score=total_score,
            risk_level=risk_level,
            ten_year_risk_percentage=risk_percentage,
            risk_description=description,
            recommendations=recommendations,
            recommendation_citations=rec_citations,  # Citations for each recommendation
            evidence_citations=general_citations,     # General FINDRISC evidence
            supporting_evidence=evidence
        )
    
    def _get_risk_category(self, score: int):
        for score_range, (level, percentage, desc) in self.RISK_CATEGORIES.items():
            if score_range[0] <= score <= score_range[1]:
                return level, percentage, desc
        return DiabetesRiskLevel.VERY_HIGH, 50.0, "Score outside validated range"
        
    def _generate_recommendations(self, score: int, bmi: float, patient_data: Dict) -> Tuple[List[str], List[str]]:
        """Generate evidence-based recommendations with direct citations from knowledge base."""
        
        recommendations = []
        citations = []
        
        try:
            from knowledge_base import MedicalSearchEngine
            
            with MedicalSearchEngine() as engine:
                # Get FINDRISC-specific evidence first
                findrisc_evidence = engine.search_by_calculator("FINDRISC", limit=5)
                
                # Build evidence-backed recommendations based on risk level
                if score >= 15:  # High/Very High Risk
                    high_risk_recs, high_risk_cites = self._get_high_risk_evidence(engine, findrisc_evidence)
                    recommendations.extend(high_risk_recs)
                    citations.extend(high_risk_cites)
                    
                elif score >= 12:  # Moderate Risk
                    moderate_recs, moderate_cites = self._get_moderate_risk_evidence(engine, findrisc_evidence)
                    recommendations.extend(moderate_recs)
                    citations.extend(moderate_cites)
                
                # Lifestyle-specific evidence retrieval
                if bmi and bmi >= 25:
                    weight_recs, weight_cites = self._get_weight_management_evidence(engine)
                    recommendations.extend(weight_recs)
                    citations.extend(weight_cites)
                
                if not patient_data.get('physical_activity', True):
                    activity_recs, activity_cites = self._get_physical_activity_evidence(engine)
                    recommendations.extend(activity_recs)
                    citations.extend(activity_cites)
                
                if not patient_data.get('vegetable_fruit_daily', True):
                    diet_recs, diet_cites = self._get_dietary_evidence(engine)
                    recommendations.extend(diet_recs)
                    citations.extend(diet_cites)
                    
                # Follow-up recommendations with evidence
                followup_recs, followup_cites = self._get_followup_evidence(engine, score)
                recommendations.extend(followup_recs)
                citations.extend(followup_cites)
                    
        except Exception as e:
            print(f"Warning: Knowledge base unavailable ({e}), using evidence-based fallbacks")
            recommendations, citations = self._get_fallback_evidence_recommendations(score, bmi, patient_data)
        
        # Remove duplicates while preserving order
        unique_recommendations = list(dict.fromkeys(recommendations))
        unique_citations = list(dict.fromkeys(citations))
        
        return unique_recommendations, unique_citations

    def _get_high_risk_evidence(self, engine, findrisc_evidence: List) -> Tuple[List[str], List[str]]:
        """Extract high-risk recommendations from knowledge base evidence."""
        
        recommendations = []
        citations = []
        
        # Search for diabetes screening evidence
        screening_results = engine.search_medical_content(
            "diabetes screening HbA1c fasting glucose ADA", 
            content_type="MedicalGuideline", 
            limit=2
        )
        
        for result in screening_results:
            if any(term in result.content.lower() for term in ['hba1c', 'screening', 'glucose']):
                recommendations.append(
                    f"Schedule comprehensive diabetes screening (HbA1c, fasting glucose) per {result.organization} guidelines"
                )
                citations.append(result.citation)
                break
        
        # Search for prevention program evidence
        prevention_results = engine.search_medical_content(
            "diabetes prevention program lifestyle intervention", 
            limit=2
        )
        
        for result in prevention_results:
            if any(term in result.content.lower() for term in ['prevention', 'program', 'intervention']):
                recommendations.append(
                    f"Consider structured diabetes prevention program based on {result.organization or result.journal} evidence"
                )
                citations.append(result.citation)
                break
        
        # Ensure we have at least basic evidence-backed recommendations
        if not recommendations:
            recommendations = [
                "Schedule diabetes screening with HbA1c and fasting glucose testing",
                "Referral to evidence-based diabetes prevention program"
            ]
            citations = [
                "American Diabetes Association. Standards of Medical Care in Diabetes—2024. Diabetes Care. 2024;47(Suppl 1):S1-S321."
            ]
        
        return recommendations, citations

    def _get_moderate_risk_evidence(self, engine, findrisc_evidence: List) -> Tuple[List[str], List[str]]:
        """Extract moderate-risk recommendations from knowledge base evidence."""
        
        recommendations = []
        citations = []
        
        # Search for lifestyle intervention evidence
        lifestyle_results = engine.search_medical_content(
            "lifestyle modification diabetes prevention structured program", 
            limit=2
        )
        
        for result in lifestyle_results:
            if any(term in result.content.lower() for term in ['lifestyle', 'modification', 'intervention']):
                recommendations.append(
                    f"Implement structured lifestyle modification program per {result.organization or result.journal} recommendations"
                )
                citations.append(result.citation)
                break
        
        if not recommendations:
            recommendations = ["Implement evidence-based lifestyle modification program"]
            citations = ["Diabetes Prevention Program Research Group. N Engl J Med. 2002;346(6):393-403."]
        
        return recommendations, citations

    def _get_weight_management_evidence(self, engine) -> Tuple[List[str], List[str]]:
        """Retrieve evidence-based weight management recommendations."""
        
        results = engine.search_medical_content("weight loss diabetes prevention 5% 7%", limit=2)
        recommendations = []
        citations = []
        
        for result in results:
            content_lower = result.content.lower()
            if any(term in content_lower for term in ['weight loss', 'weight reduction', '5%', '7%']):
                # Extract specific targets from evidence
                if '7%' in content_lower:
                    recommendations.append(
                        f"Target 7% weight reduction based on {result.organization or result.journal} evidence"
                    )
                elif '5%' in content_lower:
                    recommendations.append(
                        f"Target 5-10% weight reduction per {result.organization or result.journal} guidelines"
                    )
                citations.append(result.citation)
                break
        
        if not recommendations:
            recommendations = ["Target 7% weight reduction through structured intervention"]
            citations = ["Diabetes Prevention Program Research Group. N Engl J Med. 2002;346(6):393-403."]
        
        return recommendations, citations

    def _get_physical_activity_evidence(self, engine) -> Tuple[List[str], List[str]]:
        """Retrieve evidence-based physical activity recommendations."""
        
        results = engine.search_medical_content("physical activity 150 minutes moderate exercise ADA", limit=2)
        recommendations = []
        citations = []
        
        for result in results:
            if '150' in result.content and any(term in result.content.lower() for term in ['physical', 'activity', 'exercise']):
                recommendations.append(
                    f"Begin 150 minutes/week moderate physical activity per {result.organization or result.journal} guidelines"
                )
                citations.append(result.citation)
                break
        
        if not recommendations:
            recommendations = ["Begin moderate physical activity: 150 minutes/week"]
            citations = ["American Diabetes Association. Standards of Medical Care in Diabetes—2024."]
        
        return recommendations, citations

    def _get_dietary_evidence(self, engine) -> Tuple[List[str], List[str]]:
        """Retrieve evidence-based dietary recommendations."""
        
        results = engine.search_medical_content("dietary fiber vegetables fruits diabetes prevention", limit=2)
        recommendations = []
        citations = []
        
        for result in results:
            content_lower = result.content.lower()
            if any(term in content_lower for term in ['fiber', 'vegetables', 'fruits', 'diet']):
                recommendations.append(
                    f"Increase dietary fiber and vegetable intake per {result.organization or result.journal} recommendations"
                )
                citations.append(result.citation)
                break
        
        if not recommendations:
            recommendations = ["Increase fiber intake: 5+ servings vegetables/fruits daily"]
            citations = ["American Diabetes Association. Standards of Medical Care in Diabetes—2024."]
        
        return recommendations, citations

    def _get_followup_evidence(self, engine, score: int) -> Tuple[List[str], List[str]]:
        """Retrieve evidence-based follow-up recommendations."""
        
        recommendations = []
        citations = []
        
        if score <= 7:
            # Search for low-risk follow-up evidence
            results = engine.search_medical_content("diabetes screening interval normal risk 3 years", limit=1)
            if results and '3' in results[0].content:
                recommendations.append(f"Reassess diabetes risk every 3 years per {results[0].organization} guidelines")
                citations.append(results[0].citation)
            else:
                recommendations.append("Reassess diabetes risk every 3 years")
                citations.append("US Preventive Services Task Force. JAMA. 2021;326(8):736-743.")
        else:
            # Annual reassessment for elevated risk
            results = engine.search_medical_content("diabetes risk annual reassessment ADA", limit=1)
            if results:
                recommendations.append(f"Annual diabetes risk reassessment per {results[0].organization} guidelines")
                citations.append(results[0].citation)
            else:
                recommendations.append("Annual diabetes risk reassessment recommended")
                citations.append("American Diabetes Association. Standards of Medical Care in Diabetes—2024.")
        
        return recommendations, citations

    def _get_fallback_evidence_recommendations(self, score: int, bmi: float, patient_data: Dict) -> Tuple[List[str], List[str]]:
        """Evidence-based fallback recommendations with proper citations when KB unavailable."""
        
        recommendations = []
        citations = []
        
        # High-risk evidence-based recommendations
        if score >= 15:
            recommendations.extend([
                "Schedule comprehensive diabetes screening (HbA1c, fasting glucose, 2-hour OGTT)",
                "Urgent referral to structured diabetes prevention program"
            ])
            citations.extend([
                "American Diabetes Association. Standards of Medical Care in Diabetes—2024. Diabetes Care. 2024;47(Suppl 1):S1-S321.",
                "Diabetes Prevention Program Research Group. N Engl J Med. 2002;346(6):393-403."
            ])
        elif score >= 12:
            recommendations.append("Implement structured lifestyle modification program")
            citations.append("Lindström J, Tuomilehto J. Diabetes Care. 2003;26(3):725-731.")
        
        # Personalized evidence-based recommendations
        if bmi and bmi >= 25:
            recommendations.append("Target 7% weight reduction through structured intervention")
            citations.append("Diabetes Prevention Program Research Group. N Engl J Med. 2002;346(6):393-403.")
        
        if not patient_data.get('physical_activity', True):
            recommendations.append("Begin moderate physical activity: 150 minutes/week")
            citations.append("American Diabetes Association. Standards of Medical Care in Diabetes—2024.")
        
        if not patient_data.get('vegetable_fruit_daily', True):
            recommendations.append("Increase dietary fiber: 5+ servings vegetables/fruits daily")
            citations.append("American Diabetes Association. Standards of Medical Care in Diabetes—2024.")
        
        # Follow-up with evidence
        if score <= 7:
            recommendations.append("Reassess diabetes risk every 3 years")
            citations.append("US Preventive Services Task Force. JAMA. 2021;326(8):736-743.")
        else:
            recommendations.append("Annual diabetes risk reassessment recommended")
            citations.append("American Diabetes Association. Standards of Medical Care in Diabetes—2024.")
        
        return recommendations, citations
            
    def _get_supporting_evidence(self):
        """Retrieve FINDRISC evidence from knowledge base with guaranteed foundational citations."""
        # Always start with foundational citations to ensure they are present
        foundational_citations = [
            "Lindström J, Tuomilehto J. The diabetes risk score: a practical tool to predict type 2 diabetes risk. Diabetes Care. 2003;26(3):725-731.",
            "American Diabetes Association. Standards of Medical Care in Diabetes—2024. Diabetes Care. 2024;47(Suppl 1):S1-S321."
        ]
        
        citations = list(foundational_citations)  # Start with guaranteed foundational citations
        evidence = []  # KB evidence objects
        
        try:
            from knowledge_base import MedicalSearchEngine
            with MedicalSearchEngine() as engine:
                results = engine.search_by_calculator("FINDRISC", limit=3)
                
                if results:
                    for result in results:
                        # Add KB citation only if not already present (avoid duplicates)
                        if result.citation not in citations:
                            citations.append(result.citation)
                        
                        # Always add KB evidence objects for rich context
                        evidence.append({
                            "title": result.title,
                            "organization": result.organization,
                            "journal": result.journal,
                            "year": result.publication_year,
                            "citation": result.citation,
                            "content_preview": result.content[:200] + "..." if len(result.content) > 200 else result.content
                        })
                        
        except Exception as e:
            print(f"Warning: Knowledge base unavailable ({e}), using foundational citations")
        
        # Remove any remaining duplicates while preserving order
        unique_citations = []
        seen = set()
        for citation in citations:
            if citation not in seen:
                unique_citations.append(citation)
                seen.add(citation)
        
        return unique_citations, evidence

# Quick testing function
def demo_findrisc():
    """Demonstrate FINDRISC calculator with test scenario."""
    try:
        from data_models.patient_data import PatientData, get_test_scenarios
        
        calculator = FINDRISCCalculator()
        scenarios = get_test_scenarios()
        patient = PatientData.from_dict(scenarios['high_risk_middle_aged_male'])
        
        # Validate patient data
        errors = patient.validate()
        if errors:
            print(" Patient validation failed:")
            for error in errors:
                print(f"   {error}")
            return
        
        # Calculate FINDRISC
        result = calculator.calculate_findrisc(patient.to_calculator_dict())
        
        print(" FINDRISC Diabetes Risk Assessment")
        print("=" * 45)
        print(f"Patient: {patient.summary()}")
        print(f"Total Score: {result.total_score}/26")
        print(f"Risk Level: {result.risk_level.value.upper()}")
        print(f"10-Year Risk: {result.ten_year_risk_percentage}%")
        print(f"Description: {result.risk_description}")
        
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec}")
        
        print(f"\nEvidence Citations: {len(result.evidence_citations)} sources")
        
    except ImportError as e:
        print(f" Import error: {e}")
        print("Ensure data_models/patient_data.py is implemented first")
    except Exception as e:
        print(f" Calculation error: {e}")

if __name__ == "__main__":
    demo_findrisc()