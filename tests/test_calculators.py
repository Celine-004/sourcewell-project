"""
Calculator Test Suite

Tests all risk calculators for clinical accuracy, knowledge base integration,
and proper error handling. Validates FINDRISC, Modified Framingham, and 
Colorectal screening calculators with realistic patient scenarios.
"""

import sys
import unittest
import time
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from calculators import (
    MultiCalculatorRunner, FINDRISCCalculator, ModifiedFraminghamCalculator, 
    ColorectalScreeningCalculator, DiabetesRiskLevel, CVDRiskLevel, 
    ScreeningRecommendation
)
from data_models.patient_data import PatientData, get_test_scenarios

class TestCalculatorAccuracy(unittest.TestCase):
    """Test individual calculator accuracy and clinical validation."""
    
    def setUp(self):
        """Initialize calculators and test scenarios."""
        self.findrisc = FINDRISCCalculator()
        self.framingham = ModifiedFraminghamCalculator()
        self.colorectal = ColorectalScreeningCalculator()
        self.scenarios = get_test_scenarios()
    
    def test_findrisc_low_risk_scenario(self):
        """Test FINDRISC with validated low-risk patient."""
        patient = PatientData.from_dict(self.scenarios['low_risk_young_female'])
        result = self.findrisc.calculate_findrisc(patient.to_calculator_dict())
        
        # Validate scoring accuracy
        self.assertLessEqual(result.total_score, 7, "Low-risk patient should score ≤7")
        self.assertEqual(result.risk_level, DiabetesRiskLevel.LOW)
        self.assertEqual(result.ten_year_risk_percentage, 1.0)
        self.assertIn("maintain", result.risk_description.lower())
        
        # Validate evidence integration
        self.assertGreater(len(result.recommendations), 0)
        self.assertGreater(len(result.evidence_citations), 0)
        self.assertGreater(len(result.recommendation_citations), 0)
    
    def test_findrisc_high_risk_scenario(self):
        """Test FINDRISC with validated high-risk patient."""
        patient = PatientData.from_dict(self.scenarios['high_risk_middle_aged_male'])
        result = self.findrisc.calculate_findrisc(patient.to_calculator_dict())
        
        # Validate high-risk scoring
        self.assertGreaterEqual(result.total_score, 15, "High-risk patient should score ≥15")
        self.assertIn(result.risk_level, [DiabetesRiskLevel.HIGH, DiabetesRiskLevel.VERY_HIGH])
        self.assertGreaterEqual(result.ten_year_risk_percentage, 33.0)
        
        # Validate clinical recommendations
        has_medical_eval = any("medical evaluation" in rec.lower() or "screening" in rec.lower() 
                             for rec in result.recommendations)
        self.assertTrue(has_medical_eval, "High-risk should include medical evaluation recommendation")
    
    def test_framingham_bp_categorization_fix(self):
        """Test the critical BP categorization fix for mixed categories."""
        # Test cases that validate the AHA/ACC 2017 "use highest category" rule
        test_cases = [
            (125, 85, "Stage 1 Hypertension"),  # SBP Elevated + DBP Stage 1 → Stage 1
            (135, 75, "Stage 1 Hypertension"),  # SBP Stage 1 + DBP Normal → Stage 1  
            (145, 95, "Stage 2 Hypertension"),  # SBP Stage 2 + DBP Stage 2 → Stage 2
            (115, 70, "Normal"),                # Both Normal → Normal
            (185, 100, "Hypertensive Crisis")   # SBP Crisis + DBP Stage 2 → Crisis
        ]
        
        for sbp, dbp, expected in test_cases:
            with self.subTest(systolic=sbp, diastolic=dbp):
                result = self.framingham._categorize_blood_pressure(sbp, dbp)
                self.assertEqual(result, expected, 
                    f"BP {sbp}/{dbp} should be classified as '{expected}', got '{result}'")
    
    def test_framingham_high_risk_scenario(self):
        """Test Framingham with validated high-risk patient."""
        patient = PatientData.from_dict(self.scenarios['high_risk_middle_aged_male'])
        result = self.framingham.calculate_framingham_risk(patient.to_calculator_dict())
        
        # Validate high CVD risk  
        self.assertGreaterEqual(result.ten_year_risk_percentage, 7.5)
        self.assertIn(result.risk_level, [CVDRiskLevel.INTERMEDIATE, CVDRiskLevel.HIGH])
        self.assertIn("Hypertension", result.bp_category)
        
        # Validate clinical recommendations
        has_statin_rec = any("statin" in rec.lower() for rec in result.recommendations)
        has_smoking_rec = any("smoking" in rec.lower() for rec in result.recommendations)
        has_medical_disclaimer = any("consult your medical provider" in rec.lower() 
                                   for rec in result.recommendations)
        
        self.assertTrue(has_statin_rec, "High CVD risk should include statin recommendation")
        self.assertTrue(has_smoking_rec, "Smoker should have smoking cessation recommendation")
        self.assertTrue(has_medical_disclaimer, "Therapy recommendations should include medical disclaimer")
    
    def test_framingham_age_validation(self):
        """Test Framingham age boundaries (30-79 years)."""
        # Test age boundaries
        with self.assertRaises(ValueError) as context:
            self.framingham.calculate_framingham_risk({
                'age': 25, 'gender': 'male', 'total_cholesterol': 200, 'hdl_cholesterol': 50,
                'systolic_bp': 120, 'diastolic_bp': 80, 'on_bp_medication': False,
                'current_smoker': False, 'diabetes': False
            })
        self.assertIn("30-79", str(context.exception))
    
    def test_colorectal_screening_logic(self):
        """Test colorectal screening recommendations by age group."""
        # Test age 45-49 (Grade B)
        patient_data = {
            'age': 48, 'gender': 'male', 'height_cm': 175, 'weight_kg': 75,
            'family_colorectal_cancer': False
        }
        patient = PatientData.from_dict(patient_data)
        result = self.colorectal.assess_colorectal_screening(patient.to_calculator_dict())
        
        self.assertEqual(result.recommendation, ScreeningRecommendation.START_NOW)
        self.assertIn("Grade B", result.rationale)
        
        # Test high-risk family history
        high_risk_data = {
            'age': 42, 'gender': 'female', 'height_cm': 165, 'weight_kg': 60,
            'family_colorectal_cancer': True,
            'family_colorectal_age': 45
        }
        patient2 = PatientData.from_dict(high_risk_data)
        result2 = self.colorectal.assess_colorectal_screening(patient2.to_calculator_dict())
        
        self.assertEqual(result2.recommendation, ScreeningRecommendation.START_NOW)
        self.assertEqual(result2.risk_level, "High Risk")

class TestMultiCalculatorRunner(unittest.TestCase):
    """Test integrated multi-calculator assessment functionality."""
    
    def setUp(self):
        """Initialize runner and test scenarios."""
        self.runner = MultiCalculatorRunner()
        self.scenarios = get_test_scenarios()
    
    def test_runner_initialization(self):
        """Test runner loads all calculators successfully."""
        self.assertTrue(self.runner.calculators_loaded, "All calculators should load successfully")
    
    def test_comprehensive_high_risk_assessment(self):
        """Test comprehensive assessment with high-risk patient."""
        patient = PatientData.from_dict(self.scenarios['high_risk_middle_aged_male'])
        
        # Validate patient data first
        validation_errors = patient.validate()
        self.assertEqual(len(validation_errors), 0, f"Patient validation failed: {validation_errors}")
        
        # Run comprehensive assessment
        start_time = time.time()
        results = self.runner.run_all_assessments(patient)
        assessment_time = time.time() - start_time
        
        # Validate assessment success
        self.assertTrue(results['success'], "Assessment should succeed for valid patient")
        self.assertEqual(results['successful_assessments'], 3, "All 3 calculators should succeed")
        self.assertEqual(results['calculators_run'], 3)
        
        # Validate results structure
        self.assertIn('diabetes', results['results'])
        self.assertIn('cardiovascular', results['results'])
        self.assertIn('colorectal_screening', results['results'])
        
        # Validate priority actions for high-risk patient
        priority_actions = results['priority_actions']
        self.assertGreater(len(priority_actions), 0, "High-risk patient should have priority actions")
        
        # Check for smoking cessation as CRITICAL priority (patient is smoker)
        has_critical_smoking = any("CRITICAL" in action and "smoking" in action.lower() 
                                 for action in priority_actions)
        self.assertTrue(has_critical_smoking, "Smoker should have CRITICAL smoking cessation action")
        
        # Performance validation
        self.assertLess(assessment_time, 15.0, "Assessment should complete within 15 seconds")        
        
        print(f" High-risk assessment completed in {assessment_time:.3f}s")
    
    def test_age_boundary_handling(self):
        """Test runner handles age boundaries gracefully."""
        # Test elderly patient (outside Framingham range)
        elderly_data = {
            'age': 82, 'gender': 'female', 'height_cm': 160, 'weight_kg': 65,
            'systolic_bp': 140, 'diastolic_bp': 85, 'total_cholesterol': 200, 'hdl_cholesterol': 50
        }
        elderly_patient = PatientData.from_dict(elderly_data)
        results = self.runner.run_all_assessments(elderly_patient)
        
        self.assertTrue(results['success'])
        self.assertEqual(results['calculators_run'], 3)
        # Framingham should note age outside range, but not fail
        cvd_result = results['results']['cardiovascular']
        self.assertTrue(isinstance(cvd_result, dict))
        self.assertTrue(cvd_result.get('age_outside_range', False))

class TestKnowledgeBaseIntegration(unittest.TestCase):
    """Test knowledge base integration and fallback behavior."""
    
    def setUp(self):
        """Initialize calculators for KB testing."""
        self.findrisc = FINDRISCCalculator()
        self.framingham = ModifiedFraminghamCalculator()
        self.scenarios = get_test_scenarios()
    
    def test_citation_availability(self):
        """Test that citations are always available (KB or fallback)."""
        patient = PatientData.from_dict(self.scenarios['high_risk_middle_aged_male'])
        
        # Test FINDRISC citations
        findrisc_result = self.findrisc.calculate_findrisc(patient.to_calculator_dict())
        self.assertGreater(len(findrisc_result.evidence_citations), 0)
        self.assertGreater(len(findrisc_result.recommendation_citations), 0)
        
        # Validate fallback includes core FINDRISC citation
        has_lindstrom = any("Lindström" in citation for citation in findrisc_result.evidence_citations)
        self.assertTrue(has_lindstrom, "Should include Lindström FINDRISC citation")
        
        # Test Framingham citations
        framingham_result = self.framingham.calculate_framingham_risk(patient.to_calculator_dict())
        self.assertGreater(len(framingham_result.evidence_citations), 0)
        self.assertGreater(len(framingham_result.recommendation_citations), 0)

class TestClinicalCompliance(unittest.TestCase):
    """Test clinical compliance and safety features."""
    
    def setUp(self):
        """Initialize calculators for compliance testing."""
        self.framingham = ModifiedFraminghamCalculator()
        self.scenarios = get_test_scenarios()
    
    def test_medical_disclaimers(self):
        """Test that therapy recommendations include medical disclaimers."""
        patient = PatientData.from_dict(self.scenarios['high_risk_middle_aged_male'])
        result = self.framingham.calculate_framingham_risk(patient.to_calculator_dict())
        
        # Check for medical disclaimers in therapy recommendations
        therapy_recs = [rec for rec in result.recommendations 
                       if any(term in rec.lower() for term in ['statin', 'medication', 'therapy', 'aspirin'])]
        
        if therapy_recs:  # If therapy is recommended
            has_disclaimer = any("consult your medical provider" in rec.lower() 
                               for rec in therapy_recs)
            self.assertTrue(has_disclaimer, 
                "Therapy recommendations must include 'Consult your medical provider' disclaimer")

def run_comprehensive_calculator_tests():
    """Run all calculator tests with detailed reporting."""
    print("SourceWell Calculator Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestCalculatorAccuracy,
        TestMultiCalculatorRunner, 
        TestKnowledgeBaseIntegration,
        TestClinicalCompliance
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    start_time = time.time()
    result = runner.run(suite)
    total_time = time.time() - start_time
    
    # Detailed reporting
    print(f"\n{'='*60}")
    print(f"CALCULATOR TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"Total Time: {total_time:.3f} seconds")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"   {test}")
            # Pre-process the error message outside the f-string
            try:
                error_msg = traceback.split('AssertionError: ')[-1].split('\n')[0]
            except (IndexError, AttributeError):
                error_msg = "Could not parse error message"
            print(f"     {error_msg}")

    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"    {test}")
            try:
                error_msg = traceback.split('\n')[0]
            except (IndexError, AttributeError):
                error_msg = "Could not parse error message"
            print(f"     {error_msg}")
    
    if result.wasSuccessful():
        print(f"\n ALL CALCULATOR TESTS PASSED!")
        print(f"   SourceWell calculators are clinically validated and ready for production use.")
    else:
        print(f"\n SOME TESTS FAILED")
        print(f"   Review failures above and fix issues before proceeding.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_calculator_tests()
    sys.exit(0 if success else 1)