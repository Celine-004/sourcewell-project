"""
Colorectal Cancer Screening Recommendations

USPSTF 2021 guideline-based screening recommendations with risk stratification
and evidence-based screening interval management.
Based on: US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977.
"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class ScreeningRecommendation(Enum):
    START_NOW = "start_now"
    CONTINUE = "continue" 
    DISCUSS = "discuss"
    NOT_RECOMMENDED = "not_recommended"
    HIGH_RISK_REFERRAL = "high_risk_referral"

class ScreeningMethod(Enum):
    COLONOSCOPY = "colonoscopy"
    FIT = "fit"  # Fecal immunochemical test
    COLOGUARD = "cologuard"  # Stool DNA
    FLEXIBLE_SIG = "flexible_sigmoidoscopy"

@dataclass
class ColorectalResult:
    recommendation: ScreeningRecommendation
    recommended_methods: List[ScreeningMethod]
    screening_interval: str
    risk_level: str
    rationale: str
    next_screening_date: Optional[str]
    recommendations: List[str]
    recommendation_citations: List[str]
    evidence_citations: List[str]
    supporting_evidence: List[Dict]

class ColorectalScreeningCalculator:

    # Standard screening intervals per USPSTF 2021
    SCREENING_INTERVALS = {
        ScreeningMethod.COLONOSCOPY: 10,
        ScreeningMethod.FIT: 1,
        ScreeningMethod.COLOGUARD: 3,
        ScreeningMethod.FLEXIBLE_SIG: 5
    }
    
    def assess_colorectal_screening(self, patient_data: Dict[str, Any]) -> ColorectalResult:
        """Assess colorectal cancer screening recommendations based on USPSTF 2021 guidelines."""
        
        # Extract patient data
        age = patient_data.get('age')
        gender = patient_data.get('gender', '').lower()
        family_history = patient_data.get('family_history_first_degree', False)
        family_age = patient_data.get('family_history_age')
        personal_polyps = patient_data.get('personal_history_polyps', False)
        ibd = patient_data.get('inflammatory_bowel_disease', False)
        high_risk_syndrome = patient_data.get('high_risk_syndrome', False)
        previous_date = patient_data.get('previous_screening_date')
        previous_method = patient_data.get('previous_screening_method')
        
        # Validation
        if not (18 <= age <= 100):
            raise ValueError("Age must be between 18-100 years")
        if gender not in ['male', 'female']:
            raise ValueError("Gender must be 'male' or 'female'")
        
        # High-risk conditions require specialized management
        if high_risk_syndrome or ibd:
            return self._high_risk_recommendation()
        
        risk_level = self._assess_risk_level(age, family_history, family_age, personal_polyps)
        
        # Age-based screening recommendations following USPSTF guidelines
        if age < 45:
            return self._under_45_recommendation(risk_level, family_history, family_age)
        elif 45 <= age <= 49:
            return self._age_45_49_recommendation(risk_level, previous_date, previous_method)
        elif 50 <= age <= 75:
            return self._age_50_75_recommendation(risk_level, previous_date, previous_method)
        elif 76 <= age <= 85:
            return self._age_76_85_recommendation(previous_date)
        else:  # age > 85
            return self._over_85_recommendation()
    
    def _assess_risk_level(self, age: int, family_history: bool, 
                          family_age: Optional[int], personal_polyps: bool) -> str:
        if personal_polyps:
            return "Increased Surveillance"
        
        if family_history:
            if family_age and family_age < 50:
                return "High Risk"
            elif family_age and family_age < 60:
                return "Increased Risk"
            else:
                return "Slightly Increased Risk"
        
        return "Average Risk"
    
    def _under_45_recommendation(self, risk_level: str, family_history: bool,
                               family_age: Optional[int]) -> ColorectalResult:
        """Screening recommendations for adults under 45."""
        
        if risk_level == "High Risk" or (family_history and family_age and family_age < 50):
            recommendations, rec_citations = self._get_high_risk_under_45_evidence()
            evidence_citations, evidence = self._get_supporting_evidence()
            
            return ColorectalResult(
                recommendation=ScreeningRecommendation.START_NOW,
                recommended_methods=[ScreeningMethod.COLONOSCOPY],
                screening_interval="Every 5-10 years (individualized)",
                risk_level="High Risk",
                rationale=f"Family history of early-onset colorectal cancer (age {family_age}) requires earlier screening",
                next_screening_date=self._calculate_next_date(5),
                recommendations=recommendations,
                recommendation_citations=rec_citations,
                evidence_citations=evidence_citations,
                supporting_evidence=evidence
            )
            
        elif risk_level in ["Increased Risk", "Slightly Increased Risk"]:
            recommendations, rec_citations = self._get_increased_risk_under_45_evidence()
            evidence_citations, evidence = self._get_supporting_evidence()
            
            return ColorectalResult(
                recommendation=ScreeningRecommendation.DISCUSS,
                recommended_methods=[ScreeningMethod.COLONOSCOPY, ScreeningMethod.FIT],
                screening_interval="Discuss with provider",
                risk_level="Increased Risk",
                rationale="Family history present - consider early screening discussion",
                next_screening_date=None,
                recommendations=recommendations,
                recommendation_citations=rec_citations,
                evidence_citations=evidence_citations,
                supporting_evidence=evidence
            )
        
        else:
            recommendations, rec_citations = self._get_average_risk_under_45_evidence()
            evidence_citations, evidence = self._get_supporting_evidence()
            
            return ColorectalResult(
                recommendation=ScreeningRecommendation.NOT_RECOMMENDED,
                recommended_methods=[],
                screening_interval="Begin at age 45",
                risk_level="Average Risk",
                rationale="Standard screening begins at age 45 for average-risk individuals",
                next_screening_date=None,
                recommendations=recommendations,
                recommendation_citations=rec_citations,
                evidence_citations=evidence_citations,
                supporting_evidence=evidence
            )
    
    def _age_45_49_recommendation(self, risk_level: str, previous_date: Optional[str],
                                 previous_method: Optional[str]) -> ColorectalResult:
        """Screening recommendations for ages 45-49 (USPSTF Grade B)."""
        
        # Check if screening is current
        if previous_date and previous_method:
            is_current, next_date = self._check_screening_status(previous_date, previous_method)
            if is_current:
                recommendations, rec_citations = self._get_continue_screening_evidence()
                evidence_citations, evidence = self._get_supporting_evidence()
                
                return ColorectalResult(
                    recommendation=ScreeningRecommendation.CONTINUE,
                    recommended_methods=self._get_method_from_string(previous_method),
                    screening_interval=self._get_interval_for_method(previous_method),
                    risk_level=risk_level,
                    rationale="Continue current screening schedule",
                    next_screening_date=next_date,
                    recommendations=recommendations,
                    recommendation_citations=rec_citations,
                    evidence_citations=evidence_citations,
                    supporting_evidence=evidence
                )
        
        recommendations, rec_citations = self._get_age_45_49_start_evidence()
        evidence_citations, evidence = self._get_supporting_evidence()
        
        return ColorectalResult(
            recommendation=ScreeningRecommendation.START_NOW,
            recommended_methods=[ScreeningMethod.COLONOSCOPY, ScreeningMethod.FIT, 
                               ScreeningMethod.COLOGUARD],
            screening_interval="Colonoscopy every 10 years OR FIT annually OR Cologuard every 3 years",
            risk_level=risk_level,
            rationale="USPSTF Grade B recommendation for ages 45-49",
            next_screening_date=self._calculate_next_date(1),
            recommendations=recommendations,
            recommendation_citations=rec_citations,
            evidence_citations=evidence_citations,
            supporting_evidence=evidence
        )
    
    def _age_50_75_recommendation(self, risk_level: str, previous_date: Optional[str],
                                 previous_method: Optional[str]) -> ColorectalResult:
        """Screening recommendations for ages 50-75 (USPSTF Grade A)."""
        
        # Check if screening is current
        if previous_date and previous_method:
            is_current, next_date = self._check_screening_status(previous_date, previous_method)
            if is_current:
                recommendations, rec_citations = self._get_continue_screening_evidence()
                evidence_citations, evidence = self._get_supporting_evidence()
                
                return ColorectalResult(
                    recommendation=ScreeningRecommendation.CONTINUE,
                    recommended_methods=self._get_method_from_string(previous_method),
                    screening_interval=self._get_interval_for_method(previous_method),
                    risk_level=risk_level,
                    rationale="Continue current screening schedule",
                    next_screening_date=next_date,
                    recommendations=recommendations,
                    recommendation_citations=rec_citations,
                    evidence_citations=evidence_citations,
                    supporting_evidence=evidence
                )
        
        recommendations, rec_citations = self._get_age_50_75_start_evidence()
        evidence_citations, evidence = self._get_supporting_evidence()
        
        return ColorectalResult(
            recommendation=ScreeningRecommendation.START_NOW,
            recommended_methods=[ScreeningMethod.COLONOSCOPY, ScreeningMethod.FIT, 
                               ScreeningMethod.COLOGUARD],
            screening_interval="Colonoscopy every 10 years OR FIT annually OR Cologuard every 3 years",
            risk_level=risk_level,
            rationale="USPSTF Grade A recommendation for ages 50-75",
            next_screening_date=self._calculate_next_date(1),
            recommendations=recommendations,
            recommendation_citations=rec_citations,
            evidence_citations=evidence_citations,
            supporting_evidence=evidence
        )
    
    def _age_76_85_recommendation(self, previous_date: Optional[str]) -> ColorectalResult:
        """Screening recommendations for ages 76-85 (USPSTF Grade C)."""
        
        recommendations, rec_citations = self._get_age_76_85_evidence()
        evidence_citations, evidence = self._get_supporting_evidence()
        
        return ColorectalResult(
            recommendation=ScreeningRecommendation.DISCUSS,
            recommended_methods=[ScreeningMethod.FIT, ScreeningMethod.COLOGUARD],
            screening_interval="Individualized decision",
            risk_level="Age-related considerations",
            rationale="USPSTF Grade C - individualize based on health status and prior screening",
            next_screening_date=None,
            recommendations=recommendations,
            recommendation_citations=rec_citations,
            evidence_citations=evidence_citations,
            supporting_evidence=evidence
        )
    
    def _over_85_recommendation(self) -> ColorectalResult:
        """Screening recommendations for adults over 85 (USPSTF Grade D)."""
        
        recommendations, rec_citations = self._get_over_85_evidence()
        evidence_citations, evidence = self._get_supporting_evidence()
        
        return ColorectalResult(
            recommendation=ScreeningRecommendation.NOT_RECOMMENDED,
            recommended_methods=[],
            screening_interval="Not recommended",
            risk_level="Age >85",
            rationale="USPSTF Grade D recommendation - screening not recommended",
            next_screening_date=None,
            recommendations=recommendations,
            recommendation_citations=rec_citations,
            evidence_citations=evidence_citations,
            supporting_evidence=evidence
        )
    
    def _high_risk_recommendation(self) -> ColorectalResult:
        """Recommendations for high-risk conditions requiring specialized care."""
        
        recommendations, rec_citations = self._get_high_risk_referral_evidence()
        evidence_citations, evidence = self._get_supporting_evidence()
        
        return ColorectalResult(
            recommendation=ScreeningRecommendation.HIGH_RISK_REFERRAL,
            recommended_methods=[ScreeningMethod.COLONOSCOPY],
            screening_interval="Specialized schedule",
            risk_level="High Risk",
            rationale="High-risk condition requires specialized gastroenterology management",
            next_screening_date=None,
            recommendations=recommendations,
            recommendation_citations=rec_citations,
            evidence_citations=evidence_citations,
            supporting_evidence=evidence
        )
    
    # Evidence-based recommendation methods
    def _get_high_risk_under_45_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = []
        citations = []
        
        try:
            from knowledge_base import MedicalSearchEngine
            with MedicalSearchEngine() as engine:
                results = engine.search_medical_content(
                    "colorectal screening early onset family history colonoscopy", 
                    content_type="MedicalGuideline", limit=2
                )
                
                for result in results:
                    if any(term in result.content.lower() for term in ['early', 'family', 'colonoscopy']):
                        recommendations.extend([
                            f"Begin colonoscopy screening per {result.organization} guidelines",
                            "Consider genetic counseling for hereditary cancer syndromes"
                        ])
                        citations.append(result.citation)
                        break
        except Exception:
            recommendations = [
                "Begin colonoscopy screening at age 40 or 10 years before family member's age",
                "Consider genetic counseling for hereditary cancer syndromes"
            ]
            citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        
        return recommendations, citations
    
    def _get_age_45_49_start_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = []
        citations = []
        
        try:
            from knowledge_base import MedicalSearchEngine
            with MedicalSearchEngine() as engine:
                results = engine.search_medical_content(
                    "colorectal screening age 45 USPSTF grade B recommendation", 
                    content_type="MedicalGuideline", limit=2
                )
                
                for result in results:
                    if any(term in result.content.lower() for term in ['45', 'screening', 'grade b']):
                        recommendations.extend([
                            f"Begin colorectal screening per {result.organization} Grade B recommendation",
                            "Choose preferred screening method: colonoscopy, FIT, or Cologuard",
                            "Discuss screening options with healthcare provider"
                        ])
                        citations.append(result.citation)
                        break
        except Exception:
            recommendations = [
                "Begin colorectal cancer screening (USPSTF Grade B recommendation)",
                "Choose screening method: colonoscopy every 10 years, FIT annually, or Cologuard every 3 years",
                "Discuss screening preferences with healthcare provider"
            ]
            citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        
        return recommendations, citations
    
    def _get_age_50_75_start_evidence(self) -> Tuple[List[str], List[str]]:
        """Get evidence for ages 50-75 screening start."""
        recommendations = []
        citations = []
        
        try:
            from knowledge_base import MedicalSearchEngine
            with MedicalSearchEngine() as engine:
                results = engine.search_medical_content(
                    "colorectal screening age 50 75 USPSTF grade A recommendation", 
                    content_type="MedicalGuideline", limit=2
                )
                
                for result in results:
                    if any(term in result.content.lower() for term in ['50', '75', 'grade a']):
                        recommendations.extend([
                            f"Begin colorectal screening per {result.organization} Grade A recommendation",
                            "Strong evidence supports multiple screening methods",
                            "Regular screening significantly reduces colorectal cancer mortality"
                        ])
                        citations.append(result.citation)
                        break
        except Exception:
            recommendations = [
                "Begin colorectal cancer screening (USPSTF Grade A recommendation)",
                "Strong evidence supports screening effectiveness in this age group",
                "Choose preferred method and maintain regular screening schedule"
            ]
            citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        
        return recommendations, citations
    
    def _get_continue_screening_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = [
            "Continue current screening method as scheduled",
            "Maintain regular screening intervals for optimal protection",
            "Contact provider if any concerning symptoms develop"
        ]
        citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        return recommendations, citations
    
    # Utility methods for screening status and intervals
    def _check_screening_status(self, previous_date: str, method: str) -> Tuple[bool, Optional[str]]:
        """Check if previous screening is still current."""
        try:
            last_screening = datetime.strptime(previous_date, "%Y-%m-%d")
            today = datetime.now()
            
            method_enum = self._method_from_string_single(method)
            interval_years = self.SCREENING_INTERVALS.get(method_enum, 1)
            
            next_due = last_screening + timedelta(days=interval_years * 365)
            is_current = today < next_due
            
            return is_current, next_due.strftime("%Y-%m-%d") if is_current else None
            
        except (ValueError, TypeError):
            return False, None
    
    def _get_method_from_string(self, method: str) -> List[ScreeningMethod]:
        """Convert string method to ScreeningMethod enum list."""
        method_map = {
            'colonoscopy': ScreeningMethod.COLONOSCOPY,
            'fit': ScreeningMethod.FIT,
            'cologuard': ScreeningMethod.COLOGUARD,
            'flexible_sigmoidoscopy': ScreeningMethod.FLEXIBLE_SIG
        }
        return [method_map.get(method.lower(), ScreeningMethod.COLONOSCOPY)]
    
    def _method_from_string_single(self, method: str) -> ScreeningMethod:
        """Convert string method to single ScreeningMethod enum."""
        method_map = {
            'colonoscopy': ScreeningMethod.COLONOSCOPY,
            'fit': ScreeningMethod.FIT,
            'cologuard': ScreeningMethod.COLOGUARD,
            'flexible_sigmoidoscopy': ScreeningMethod.FLEXIBLE_SIG
        }
        return method_map.get(method.lower(), ScreeningMethod.COLONOSCOPY)
    
    def _get_interval_for_method(self, method: str) -> str:
        intervals = {
            'colonoscopy': "Every 10 years",
            'fit': "Annually", 
            'cologuard': "Every 3 years",
            'flexible_sigmoidoscopy': "Every 5 years"
        }
        return intervals.get(method.lower(), "Consult provider")
    
    def _calculate_next_date(self, years: int) -> str:
        next_date = datetime.now() + timedelta(days=years * 365)
        return next_date.strftime("%Y-%m-%d")
    
    def _get_supporting_evidence(self) -> Tuple[List[str], List[Dict]]:
        """Retrieve colorectal screening evidence from knowledge base."""
        citations = []
        evidence = []
        
        try:
            from knowledge_base import MedicalSearchEngine
            with MedicalSearchEngine() as engine:
                results = engine.search_by_calculator("ColorectalScreening", limit=3)
                
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
                "US Preventive Services Task Force. Screening for Colorectal Cancer: US Preventive Services Task Force Recommendation Statement. JAMA. 2021;325(19):1965-1977.",
                "American Cancer Society. Colorectal Cancer Screening Guidelines. CA Cancer J Clin. 2018;68(4):250-281."
            ]
            print(f"Warning: Knowledge base unavailable ({e}), using fallback citations")
            
        return citations, evidence
    
    # Additional evidence methods for completeness
    def _get_increased_risk_under_45_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = ["Discuss early screening with healthcare provider", "Consider family history evaluation"]
        citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        return recommendations, citations
    
    def _get_average_risk_under_45_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = ["Begin routine screening at age 45", "Maintain healthy lifestyle to reduce cancer risk"]
        citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        return recommendations, citations
    
    def _get_age_76_85_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = [
            "Discuss benefits and risks with healthcare provider",
            "Consider overall health status and life expectancy",
            "If screening continues, prefer less invasive methods (FIT, Cologuard)"
        ]
        citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        return recommendations, citations
    
    def _get_over_85_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = [
            "Routine screening not recommended due to limited life expectancy",
            "Focus on symptom awareness and management of other health conditions"
        ]
        citations = ["US Preventive Services Task Force. JAMA. 2021;325(19):1965-1977."]
        return recommendations, citations
    
    def _get_high_risk_referral_evidence(self) -> Tuple[List[str], List[str]]:
        recommendations = [
            "URGENT: Refer to gastroenterology for specialized screening protocol",
            "High-risk conditions require individualized surveillance schedules",
            "Standard population guidelines do not apply"
        ]
        citations = ["National Comprehensive Cancer Network. Colorectal Cancer Screening Guidelines. 2024."]
        return recommendations, citations

# Demo function
def demo_colorectal():
    """Demonstrate colorectal screening calculator with comprehensive test scenarios."""
    try:
        from data_models.patient_data import PatientData, get_test_scenarios
        
        calculator = ColorectalScreeningCalculator()
        scenarios = get_test_scenarios()
        patient = PatientData.from_dict(scenarios['high_risk_middle_aged_male'])
        
        # Validate patient data
        errors = patient.validate()
        if errors:
            print(" Patient validation failed:")
            for error in errors:
                print(f"   {error}")
            return
        
        # Calculate colorectal screening recommendation
        result = calculator.assess_colorectal_screening(patient.to_calculator_dict())
        
        print(" COLORECTAL CANCER SCREENING ASSESSMENT")
        print("=" * 50)
        print(f"Patient: {patient.summary()}")
        print(f"Recommendation: {result.recommendation.value.upper()}")
        print(f"Risk Level: {result.risk_level}")
        print(f"Screening Interval: {result.screening_interval}")
        print(f"Rationale: {result.rationale}")
        
        if result.recommended_methods:
            print(f"\nRecommended Methods:")
            for method in result.recommended_methods:
                print(f"   {method.value.replace('_', ' ').title()}")
        
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec}")
        
        print(f"\nEvidence Citations: {len(result.evidence_citations)} sources")
        
    except ImportError as e:
        print(f" Import error: {e}")
    except Exception as e:
        print(f" Calculation error: {e}")

if __name__ == "__main__":
    demo_colorectal()