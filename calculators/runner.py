"""
Multi-Calculator Runner - Comprehensive Risk Assessment Orchestration

Coordinates all individual risk calculators to provide integrated preventive healthcare assessment
with evidence-based recommendations and clinical prioritization.
"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from datetime import datetime
from typing import Dict, Any, List
from data_models.patient_data import PatientData

class MultiCalculatorRunner:
    """Orchestrates all risk calculators for comprehensive patient assessment."""
    
    def __init__(self):
        """Initialize runner and load all available calculators."""
        self.calculators_loaded = False
        self._load_calculators()
    
    def _load_calculators(self):
        """Load individual calculators with comprehensive error handling and diagnostics."""
        self.calculators_loaded = False
        
        try:
            import_method = "unknown"
            
            try:
                # First attempt: Absolute imports
                from calculators.findrisc import FINDRISCCalculator
                from calculators.framingham import ModifiedFraminghamCalculator
                from calculators.colorectal import ColorectalScreeningCalculator
                import_method = "absolute"
                
            except ImportError:
                # Fallback: Relative imports
                from .findrisc import FINDRISCCalculator
                from .framingham import ModifiedFraminghamCalculator
                from .colorectal import ColorectalScreeningCalculator
                import_method = "relative"

            # Initialize calculators
            self.findrisc = FINDRISCCalculator()
            self.framingham = ModifiedFraminghamCalculator()
            self.colorectal = ColorectalScreeningCalculator()
            self.calculators_loaded = True
            
            print(f" All calculators loaded successfully using {import_method} imports")

        except ImportError as e:
            print(f"Calculator import failed: {e}")
            print("Check that calculator modules exist and are properly implemented")
        except Exception as e:
            print(f"Calculator initialization failed: {e}")
            print("Check individual calculator classes for __init__ method issues")

    def run_all_assessments(self, patient: PatientData) -> Dict[str, Any]:
        """
        Run comprehensive risk assessment for patient.
        
        Args:
            patient: Validated PatientData object
            
        Returns:
            Dictionary with comprehensive assessment results and metadata
        """
        
        validation_errors = patient.validate()
        if validation_errors:
            return {
                'success': False,
                'errors': validation_errors,
                'patient_summary': patient.summary(),
                'clinical_summary': patient.clinical_summary(),
                'assessment_date': datetime.now().isoformat()[:19]
            }
        
        if not self.calculators_loaded:
            return {
                'success': False,
                'errors': ['Calculators not loaded - check calculator modules'],
                'patient_summary': patient.summary(),
                'clinical_summary': patient.clinical_summary(),
                'assessment_date': datetime.now().isoformat()[:19]
            }
        
        results = {
            'success': True,
            'patient_summary': patient.summary(),
            'clinical_summary': patient.clinical_summary(),
            'assessment_date': datetime.now().isoformat()[:19],
            'results': {},
            'priority_actions': [],
            'integrated_risk_profile': {},
            'calculators_run': 0,
            'successful_assessments': 0
        }
        
        calc_data = patient.to_calculator_dict()
        
        # Run FINDRISC Diabetes Risk Assessment
        try:
            diabetes_result = self.findrisc.calculate_findrisc(calc_data)
            results['results']['diabetes'] = diabetes_result
            results['successful_assessments'] += 1
        except Exception as e:
            results['results']['diabetes'] = {'error': f"FINDRISC calculation failed: {str(e)}"}
        results['calculators_run'] += 1
        
        # Run Modified Framingham CVD Risk Assessment (age-gated)
        try:
            age = calc_data.get('age')
            if 30 <= age <= 79:
                cvd_result = self.framingham.calculate_framingham_risk(calc_data)
                results['results']['cardiovascular'] = cvd_result
                results['successful_assessments'] += 1
            else:
                results['results']['cardiovascular'] = {
                    'eligibility_note': f'Framingham validated for ages 30-79 (patient age: {age})',
                    'age_outside_range': True
                }
        except Exception as e:
            results['results']['cardiovascular'] = {'error': f"Framingham calculation failed: {str(e)}"}
        results['calculators_run'] += 1
        
        # Run Colorectal Cancer Screening Assessment
        try:
            screening_result = self.colorectal.assess_colorectal_screening(calc_data)
            results['results']['colorectal_screening'] = screening_result
            results['successful_assessments'] += 1
        except Exception as e:
            results['results']['colorectal_screening'] = {'error': f"Colorectal assessment failed: {str(e)}"}
        results['calculators_run'] += 1
        
        # Generate integrated clinical insights
        results['priority_actions'] = self._generate_priority_actions(results['results'])
        results['integrated_risk_profile'] = self._create_integrated_profile(results['results'])
        
        return results
    
    def _generate_priority_actions(self, assessment_results: Dict) -> List[str]:
        """Generate prioritized clinical actions with appropriate medical disclaimers."""
        priority_actions = []
        
        # Analyze diabetes risk
        diabetes = assessment_results.get('diabetes', {})
        if hasattr(diabetes, 'total_score'):
            if diabetes.total_score >= 15:
                priority_actions.append("URGENT: Diabetes screening and prevention program")
            elif diabetes.total_score >= 12:
                priority_actions.append("HIGH: Lifestyle modification for diabetes prevention")
        
        # Analyze cardiovascular risk
        cardiovascular = assessment_results.get('cardiovascular', {})
        if hasattr(cardiovascular, 'ten_year_risk_percentage'):
            if cardiovascular.ten_year_risk_percentage >= 20:
                priority_actions.append("URGENT: High-intensity cardiovascular intervention required")
            elif cardiovascular.ten_year_risk_percentage >= 7.5:
                priority_actions.append("MODERATE: Consider cardiovascular prevention measures")
            
            # Check for critical smoking intervention
            if hasattr(cardiovascular, 'recommendations'):
                smoking_recs = [rec for rec in cardiovascular.recommendations if 'smoking' in rec.lower()]
                if smoking_recs:
                    priority_actions.insert(0, "CRITICAL: Immediate smoking cessation intervention")
        
        # Screening recommendations (no medical disclaimer needed)
        screening = assessment_results.get('colorectal_screening', {})
        if hasattr(screening, 'recommendation'):
            if screening.recommendation.value == 'start_now':
                priority_actions.append("ROUTINE: Begin colorectal cancer screening")
            elif screening.recommendation.value == 'high_risk_referral':
                priority_actions.append("URGENT: Genetic counseling and high-risk screening")
        
        # Add comprehensive intervention for multiple high risks
        urgent_count = len([a for a in priority_actions if 'URGENT' in a or 'CRITICAL' in a])
        if urgent_count >= 2:
            priority_actions.insert(0, "COMPREHENSIVE: Multidisciplinary care coordination required")
        
        return priority_actions

    def _create_integrated_profile(self, assessment_results: Dict) -> Dict[str, str]:
        """Create integrated risk profile summary."""
        profile = {}
        
        # Diabetes risk summary
        diabetes = assessment_results.get('diabetes', {})
        if hasattr(diabetes, 'risk_level'):
            profile['diabetes_risk'] = f"{diabetes.risk_level.value.upper()} ({diabetes.ten_year_risk_percentage}%)"
        else:
            profile['diabetes_risk'] = "Assessment unavailable"
        
        # Cardiovascular risk summary  
        cardiovascular = assessment_results.get('cardiovascular', {})
        if hasattr(cardiovascular, 'risk_level'):
            profile['cardiovascular_risk'] = f"{cardiovascular.risk_level.value.upper()} ({cardiovascular.ten_year_risk_percentage}%)"
        elif cardiovascular.get('age_outside_range'):
            profile['cardiovascular_risk'] = "Age outside validated range (30-79)"
        else:
            profile['cardiovascular_risk'] = "Assessment unavailable"
        
        # Screening status summary
        screening = assessment_results.get('colorectal_screening', {})
        if hasattr(screening, 'recommendation'):
            profile['colorectal_screening'] = screening.recommendation.value.upper().replace('_', ' ')
        else:
            profile['colorectal_screening'] = "Assessment unavailable"
        
        return profile
    
    def print_comprehensive_report(self, results: Dict[str, Any]):
        """Print formatted comprehensive assessment report with robust type checking."""
        
        if not results['success']:
            print(" PATIENT DATA VALIDATION FAILED")
            print("-" * 40)
            for error in results['errors']:
                print(f"   {error}")
            return
        
        print(" SOURCEWELL COMPREHENSIVE RISK ASSESSMENT")
        print("=" * 65)
        print(f"Patient: {results['patient_summary']}")
        print(f"Clinical: {results['clinical_summary']}")
        print(f"Assessment: {results['assessment_date']}")
        print(f"Success Rate: {results.get('successful_assessments', 0)}/{results.get('calculators_run', 0)} calculators")
        print()
        
        # Individual assessment results
        assessment_results = results['results']
        
        # 1. Diabetes Assessment - FIXED TYPE CHECKING
        print("1. DIABETES RISK ASSESSMENT (FINDRISC)")
        print("-" * 45)
        diabetes = assessment_results.get('diabetes', {})
        if isinstance(diabetes, dict) and 'error' in diabetes:
            print(f"    Error: {diabetes['error']}")
        elif hasattr(diabetes, 'total_score'):
            print(f"   Score: {diabetes.total_score}/26 points")
            print(f"   10-Year Risk: {diabetes.ten_year_risk_percentage}%")
            print(f"   Risk Level: {diabetes.risk_level.value.upper()}")
            print(f"   Description: {diabetes.risk_description}")
            if getattr(diabetes, 'recommendations', None): 
                print(f"   Key Recommendation: {diabetes.recommendations[0]}")
        else:
            print(f"     Assessment not performed")
        print()
        
        # 2. Cardiovascular Assessment - FIXED TYPE CHECKING
        print("2. CARDIOVASCULAR RISK ASSESSMENT (FRAMINGHAM)")
        print("-" * 52)
        cardiovascular = assessment_results.get('cardiovascular', {})
        if isinstance(cardiovascular, dict) and 'error' in cardiovascular:
            print(f"    Error: {cardiovascular['error']}")
        elif isinstance(cardiovascular, dict) and cardiovascular.get('age_outside_range'): 
            print(f"     {cardiovascular['eligibility_note']}")
        elif hasattr(cardiovascular, 'ten_year_risk_percentage'): 
            print(f"   10-Year CVD Risk: {cardiovascular.ten_year_risk_percentage}%")
            print(f"   Risk Level: {cardiovascular.risk_level.value.upper()}")
            print(f"   Blood Pressure: {cardiovascular.bp_category}")
            print(f"   Description: {cardiovascular.risk_description}")
            if getattr(cardiovascular, 'recommendations', None): 
                print(f"   Key Recommendation: {cardiovascular.recommendations[0]}")
        else:
            print(f"     Assessment not performed")
        print()
        
        # 3. Screening Assessment - FIXED TYPE CHECKING
        print("3. COLORECTAL CANCER SCREENING ASSESSMENT")
        print("-" * 45)
        screening = assessment_results.get('colorectal_screening', {})
        if isinstance(screening, dict) and 'error' in screening:  
            print(f"    Error: {screening['error']}")
        elif hasattr(screening, 'recommendation'): 
            print(f"   Recommendation: {screening.recommendation.value.upper()}")
            print(f"   Risk Level: {screening.risk_level}")
            print(f"   Interval: {screening.screening_interval}")
            print(f"   Rationale: {screening.rationale}")
            if getattr(screening, 'recommended_methods', None):  
                methods = [m.value.replace('_', ' ').title() for m in screening.recommended_methods]
                print(f"   Methods: {', '.join(methods)}")
        else:
            print(f"     Assessment not performed")
        print()
        
        # Priority Actions
        if results['priority_actions']:
            print(" PRIORITY CLINICAL ACTIONS")
            print("-" * 30)
            for i, action in enumerate(results['priority_actions'], 1):
                print(f"   {i}. {action}")
            print()
        
        # Integrated Risk Profile
        if results['integrated_risk_profile']:
            print(" INTEGRATED RISK PROFILE")
            print("-" * 30)
            for domain, risk in results['integrated_risk_profile'].items():
                domain_display = domain.replace('_', ' ').title()
                print(f"    {domain_display}: {risk}")
            print()
        
        print(" COMPREHENSIVE ASSESSMENT COMPLETE")
        print("=" * 65)

# Demonstration function
def demo_runner():
    """Demonstrate the multi-calculator runner with test scenarios."""
    
    try:
        from data_models.patient_data import get_test_scenarios
        
        print("Multi-Calculator Runner Demo")
        print("=" * 50)
        
        runner = MultiCalculatorRunner()
        
        if not runner.calculators_loaded:
            print(" Cannot run demo - calculators not loaded")
            return
        
        scenarios = get_test_scenarios()
        
        # Test with high-risk scenario
        print("\n Testing with High-Risk Middle-Aged Male Scenario")
        print("-" * 55)
        patient = PatientData.from_dict(scenarios['high_risk_middle_aged_male'])
        
        results = runner.run_all_assessments(patient)
        runner.print_comprehensive_report(results)
        
        # Test with low-risk scenario for comparison
        print("\n Testing with Low-Risk Young Female Scenario")
        print("-" * 50)
        patient2 = PatientData.from_dict(scenarios['low_risk_young_female'])
        
        results2 = runner.run_all_assessments(patient2)
        runner.print_comprehensive_report(results2)
        
    except ImportError as e:
        print(f" Demo requires PatientData: {e}")
    except Exception as e:
        print(f" Demo error: {e}")

if __name__ == "__main__":
    demo_runner()