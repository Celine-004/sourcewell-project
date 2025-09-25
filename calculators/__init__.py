"""
SourceWell Risk Calculator Suite

Evidence-based risk assessment calculators for preventive healthcare with
mandatory citation verification and knowledge base integration.

Components:
- MultiCalculatorRunner: Comprehensive assessment orchestration
- FINDRISCCalculator: Finnish Diabetes Risk Score assessment
- ModifiedFraminghamCalculator: Cardiovascular risk assessment  
- ColorectalScreeningCalculator: USPSTF 2021 screening recommendations
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from .runner import MultiCalculatorRunner
from .findrisc import FINDRISCCalculator, FINDRISCResult, DiabetesRiskLevel
from .framingham import ModifiedFraminghamCalculator, FraminghamResult, CVDRiskLevel
from .colorectal import ColorectalScreeningCalculator, ColorectalResult, ScreeningRecommendation

__all__ = [
    # Primary interface - most users should use this
    'MultiCalculatorRunner',
    # Individual calculators for specialized use cases
    'FINDRISCCalculator', 'FINDRISCResult', 'DiabetesRiskLevel',
    'ModifiedFraminghamCalculator', 'FraminghamResult', 'CVDRiskLevel',
    'ColorectalScreeningCalculator', 'ColorectalResult', 'ScreeningRecommendation'
]

__version__ = "1.0.0"
__status__ = "Development - Calculators operational"
__author__ = "Selin Birinci"

# Quick system health check
def check_calculator_health():
    """Verify all calculators can be loaded successfully."""
    try:
        runner = MultiCalculatorRunner()
        return {
            'status': 'healthy' if runner.calculators_loaded else 'degraded',
            'calculators_loaded': runner.calculators_loaded,
            'available_calculators': ['FINDRISC', 'ModifiedFramingham', 'ColorectalScreening'] if runner.calculators_loaded else []
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'calculators_loaded': False
        }