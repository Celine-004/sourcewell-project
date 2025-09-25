"""
SourceWell Project Test Suite

Comprehensive testing for medical knowledge base, risk calculators,
and AI integration components.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any
from packaging.version import Version

# Ensure project root in path for test imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# SourceWell version fallback configuration
# Update FALLBACK_VERSION after reaching a stable version
FALLBACK_VERSION = "0.1.0"
FALLBACK_STATUS = "Development-Fallback"

# Version management using your centralized approach
try:
    from _version import __version__, __status__, get_version_info
    # Verify the imported function works correctly
    _ = get_version_info()
except Exception:
    __version__ = FALLBACK_VERSION
    __status__ = FALLBACK_STATUS
    
    def get_version_info():
        return {
            "platform_version": __version__,
            "status": __status__,
            "fallback_active": True
        }
    
    # Healthcare audit logging for compliance
    logging.warning(f"SourceWell version fallback activated - using v{__version__}")

# Test configuration constants
REQUIRED_CALCULATORS = ["FINDRISC", "ModifiedFramingham", "ColorectalScreening"] # if new calculator added to the app, just add it here

__all__ = [
    "validate_environment",
    "validate_content_adequacy",
    "run_full_suite", 
    "get_test_summary",
    "__version__",
    "__status__"
]

def get_content_requirements() -> Dict[str, Any]:
    """Get dynamic content requirements with smart allocation based on available content."""
    try:
        platform_version = get_version_info().get("platform_version") or __version__
        
        # Base requirements by version
        if Version(platform_version) >= Version("1.0.0"):
            target_total = 15
            baseline_guidelines = 8
        else:
            target_total = 5
            baseline_guidelines = 3
            
        # Get current content to make smart allocation decisions
        try:
            from knowledge_base import MedicalSearchEngine
            with MedicalSearchEngine() as engine:
                stats = engine.get_knowledge_base_stats()
                available_abstracts = stats.get('ResearchAbstract', 0)
                
                # Calculate smart allocation
                remaining_slots = target_total - baseline_guidelines
                abstracts_to_use = min(available_abstracts, remaining_slots)
                guidelines_needed = target_total - abstracts_to_use
                
                return {
                    "minimum_total": target_total,
                    "guidelines_minimum": guidelines_needed,
                    "abstracts_minimum": abstracts_to_use,
                    "allocation_note": f"Using {abstracts_to_use} abstracts + {guidelines_needed} guidelines = {target_total} total"
                }
                
        except Exception:
            # Fallback when database not accessible
            return {
                "minimum_total": target_total,
                "guidelines_minimum": baseline_guidelines,
                "abstracts_minimum": max(1, target_total - baseline_guidelines),
                "allocation_note": "Fallback allocation (database unavailable)"
            }
        
    except Exception:
        # Safe fallback for any errors
        return {
            "minimum_total": 5,
            "guidelines_minimum": 4,
            "abstracts_minimum": 1,
            "allocation_note": "Error fallback allocation"
        }

def validate_content_adequacy() -> Dict[str, Any]:
    """Validate content adequacy using smart healthcare AI allocation."""
    requirements = get_content_requirements()
    validation = {
        'sufficient_content': False,
        'calculator_coverage': {},
        'content_analysis': {},
        'recommendations': []
    }
    
    try:
        from knowledge_base import MedicalSearchEngine
        with MedicalSearchEngine() as engine:
            stats = engine.get_knowledge_base_stats()
            
            # Analyze current content
            total_docs = sum(stats.values())
            guidelines_count = stats.get('MedicalGuideline', 0)
            abstracts_count = stats.get('ResearchAbstract', 0)
            
            validation['content_analysis'] = {
                'total_documents': total_docs,
                'medical_guidelines': guidelines_count,
                'research_abstracts': abstracts_count,
                'requirements': requirements
            }
            
            # Check smart allocation requirements
            meets_total = total_docs >= requirements["minimum_total"]
            meets_guidelines = guidelines_count >= requirements["guidelines_minimum"]
            meets_abstracts = abstracts_count >= requirements["abstracts_minimum"]
            
            # Check calculator coverage (most important for healthcare AI)
            calculator_coverage = {}
            for calc in REQUIRED_CALCULATORS:
                results = engine.search_by_calculator(calc, limit=1)
                calculator_coverage[calc] = len(results) > 0
            
            validation['calculator_coverage'] = calculator_coverage
            covered_calculators = sum(calculator_coverage.values())
            
            # Overall adequacy assessment
            validation['sufficient_content'] = (
                meets_total and meets_guidelines and meets_abstracts and 
                covered_calculators >= 2
            )
            
            # Generate smart recommendations with allocation context
            if not validation['sufficient_content']:
                if not meets_total:
                    validation['recommendations'].append(
                        f"Need {requirements['minimum_total'] - total_docs} more documents total. "
                        f"Current: {total_docs}, Target: {requirements['minimum_total']}"
                    )
                
                if not meets_guidelines:
                    shortage = max(0, requirements['guidelines_minimum'] - guidelines_count)
                    validation['recommendations'].append(
                        f"Need {shortage} more medical guidelines. "
                        f"Current: {guidelines_count}, Smart allocation requires: {requirements['guidelines_minimum']}"
                    )
                    
                if not meets_abstracts and requirements['abstracts_minimum'] > 0:
                    shortage = max(0, requirements['abstracts_minimum'] - abstracts_count)
                    validation['recommendations'].append(
                        f"Need {shortage} more research abstracts for optimal allocation. "
                        f"Current: {abstracts_count}, Smart allocation uses: {requirements['abstracts_minimum']}"
                    )
                
                if covered_calculators < 2:
                    missing_calcs = [calc for calc, covered in calculator_coverage.items() if not covered]
                    validation['recommendations'].append(
                        f"Add content supporting calculators: {', '.join(missing_calcs)}"
                    )
            else:
                validation['recommendations'].append(
                    f" Smart allocation successful: {requirements.get('allocation_note', 'Allocation complete')}"
                )
                
    except Exception as e:
        validation['error'] = str(e)
        validation['recommendations'].append("Cannot validate content - check knowledge base connectivity")
    
    return validation

def validate_environment() -> Dict[str, Any]:
    """
    Enhanced environment validation using smart content analysis.
    
    Returns:
        Environment validation with version context
    """
    validation = {
        'platform_version': __version__,
        'platform_status': __status__,
        'ready_for_testing': False,
        'issues': []
    }
    
    try:
        from knowledge_base import check_system_health
        health = check_system_health()
        
        validation['system_health'] = health
        
        if health['operational']:
            content_check = validate_content_adequacy()
            validation.update(content_check)
            
            validation['ready_for_testing'] = validation['sufficient_content']
            
            if not validation['sufficient_content']:
                validation['issues'].extend(content_check.get('recommendations', []))
        else:
            validation['issues'] = health.get('issues', ['System not operational'])
            
    except Exception as e:
        validation['issues'].append(f"Environment validation failed: {str(e)}")
    
    return validation

def run_calculator_tests():
    """Run comprehensive calculator test suite."""
    try:
        from tests.test_calculators import run_comprehensive_calculator_tests
        return run_comprehensive_calculator_tests()
    except ImportError as e:
        print(f"Calculator tests not available: {e}")
        return False

def run_full_suite(verbose: bool = True) -> Dict[str, Any]:
    """
    Execute complete SourceWell test suite with version tracking.
    
    Returns:
        Comprehensive test results with version information
    """
    results = {
        'version': __version__,
        'status': __status__,
        'test_results': {},
        'overall_success': False
    }
    
    if verbose:
        print(f"SourceWell Healthcare AI v{__version__} - Test Suite Execution")
        print(f"   Status: {__status__}")
        print("=" * 70)
    
    # Pre-flight environment check
    env_check = validate_environment()
    if not env_check['ready_for_testing']:
        if verbose:
            print(" Environment not ready for testing:")
            for issue in env_check['issues']:
                print(f"   - {issue}")
        results['overall_success'] = False
        return results
    
    # Run test suites
    test_suites = {}
    
    # Infrastructure tests
    try:
        from tests.infrastructure_test import main as infrastructure_tests
        test_suites['infrastructure'] = infrastructure_tests() == 0
    except Exception as e:
        test_suites['infrastructure'] = False
        if verbose:
            print(f" Infrastructure tests failed: {e}")
    
    # Knowledge base tests  
    try:
        from tests.test_knowledge_base import run_comprehensive_tests
        test_suites['knowledge_base'] = run_comprehensive_tests()
    except Exception as e:
        test_suites['knowledge_base'] = False
        if verbose:
            print(f" Knowledge base tests failed: {e}")

    # NEW: Calculator tests
    try:
        test_suites['calculators'] = run_calculator_tests()
    except Exception as e:
        test_suites['calculators'] = False
        if verbose:
            print(f" Calculator tests failed: {e}")
    
    results['test_results'] = test_suites
    results['overall_success'] = all(test_suites.values())
    
    if verbose:
        print(f"\n Test Results:")
        for test_name, passed in test_suites.items():
            status = " PASS" if passed else " FAIL"
            print(f"   {test_name}: {status}")
        
        if results['overall_success']:
            print(f" SourceWell v{__version__} - All tests passed!")
        else:
            print(f"  Some tests failed. Review issues before proceeding.")
    
    return results

def get_test_summary() -> Dict[str, Any]:
    """Get summary of test capabilities and requirements."""
    try:
        version_info = get_version_info()
    except:
        version_info = {"platform_version": __version__}
    
    requirements = get_content_requirements()
    return {
        'version_info': version_info,
        'test_requirements': {
            'minimum_document_count': requirements,
            'required_calculators': REQUIRED_CALCULATORS
        },
        'test_categories': [
            'infrastructure_validation',
            'medical_content_integrity', 
            'search_functionality',
            'healthcare_compliance'
        ]
    }

def main():
    """CLI interface for automated testing and CI/CD integration."""
    import sys
    result = run_full_suite(verbose=True)
    sys.exit(0 if result.get('overall_success') else 1)

if __name__ == "__main__":
    main()
# Initialize test logging with version
logging.info(f"SourceWell Test Suite v{__version__} initialized - {__status__}")