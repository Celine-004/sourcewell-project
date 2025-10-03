# SourceWell Risk Calculator Suite

Evidence-based preventive health risk calculators with mandatory citation verification and knowledge base integration for comprehensive patient assessment.

## Overview

The SourceWell Risk Calculator Suite provides three validated clinical risk assessment tools:

- **FINDRISC Calculator**: Finnish Diabetes Risk Score for 10-year Type 2 diabetes risk assessment
- **Modified Framingham Calculator**: 10-year cardiovascular disease risk estimation with AHA/ACC guidelines
- **Colorectal Screening Calculator**: USPSTF 2021 colorectal cancer screening recommendations with risk stratification
- **Multi-Calculator Runner**: Orchestrates all calculators for comprehensive integrated assessment

All recommendations are evidence-based with dynamic citations from a knowledge base, plus robust fallbacks when the KB is unavailable.

## Key Features

- Evidence-based clinical recommendations with peer-reviewed citations
- Knowledge base integration for dynamic guideline retrieval
- Comprehensive error handling and validation
- Medical disclaimers for therapy recommendations
- Integrated risk profiling across multiple domains
- Priority action generation for clinical workflow

## Prerequisites

### System Requirements

- **Python 3.8+**: Core runtime environment
- **Project Structure**: Must run from project root directory for proper imports
- **System Path**: Project root automatically added to `sys.path` by calculator modules
- **Cross-Platform**: Code uses `pathlib.Path` for cross-platform file path handling

### Required Dependencies

- **Patient Data Model**: `data_models/patient_data.py` with `PatientData` class and validation
- **Test Scenarios**: `get_test_scenarios()` function for demonstration and testing

### Optional Components

- **Weaviate Knowledge Base**: For dynamic citation retrieval and evidence-based recommendations
- **MedicalSearchEngine**: Enhanced evidence discovery when knowledge base is available

## Quick Start

### Comprehensive Assessment (Recommended)

```bash
# Run all calculators with integrated reporting
python -m calculators.runner
```

### Individual Calculator Demos

**macOS/Linux:**

```bash
python calculators/findrisc.py     # FINDRISC diabetes risk
python calculators/framingham.py  # Framingham CVD risk  
python calculators/colorectal.py  # Colorectal screening
```

**Windows (Command Prompt):**

```cmd
python calculators\findrisc.py     # FINDRISC diabetes risk
python calculators\framingham.py  # Framingham CVD risk
python calculators\colorectal.py  # Colorectal screening
```

### Programmatic Usage

```python
from calculators import MultiCalculatorRunner
from data_models.patient_data import PatientData, get_test_scenarios

# Initialize runner and load patient data
runner = MultiCalculatorRunner()
patient = PatientData.from_dict(get_test_scenarios()['high_risk_middle_aged_male'])

# Run comprehensive assessment
results = runner.run_all_assessments(patient)
runner.print_comprehensive_report(results)
```

### Health Check

```python
from calculators import check_calculator_health
print(check_calculator_health())
```

## Clinical Calculators

### FINDRISC - Finnish Diabetes Risk Score

*Based on: Lindström & Tuomilehto, Diabetes Care 2003*

**Inputs**: Age, gender, BMI, waist circumference, physical activity, diet, hypertension medication, glucose history, family diabetes history

**Risk Categories** (Score 0-26):

- `0-7`: Low (1% 10-year risk)
- `8-11`: Slightly elevated (4%)
- `12-14`: Moderate (17%)
- `15-20`: High (33%)
- `21-26`: Very high (50%)

**Outputs**: Diabetes screening recommendations, prevention program referrals, lifestyle interventions

### Modified Framingham CVD Risk

*Based on: D'Agostino et al., Circulation 2008 + AHA/ACC 2018*

**Inputs**: Age (30-79), gender, total/HDL cholesterol, blood pressure, BP medications, smoking, diabetes

**Risk Categories** (10-year CVD risk):

- `<5%`: Low
- `5-7.4%`: Borderline
- `7.5-19.9%`: Intermediate
- `≥20%`: High

**Outputs**: Statin therapy recommendations, BP targets, smoking cessation, lifestyle modifications (*All medication recommendations include "Consult your medical provider"*)

### Colorectal Cancer Screening

*Based on: USPSTF 2021 Guidelines*

**Inputs**: Age, gender, family history, personal polyp history, IBD, previous screening

**Age-Based Recommendations**:

- `<45`: Not recommended (unless high risk)
- `45-49`: Start screening (Grade B)
- `50-75`: Routine screening (Grade A)
- `76-85`: Individualize (Grade C)
- `≥85`: Not recommended (Grade D)

**Methods**: Colonoscopy (q10y), FIT (annual), Cologuard (q3y)

## Technical Architecture

### Core Modules

- `calculators/__init__.py` - Package interface with health check
- `calculators/runner.py` - Multi-calculator orchestration and integration
- `calculators/findrisc.py` - FINDRISC diabetes risk assessment
- `calculators/framingham.py` - Modified Framingham CVD risk calculation
- `calculators/colorectal.py` - USPSTF colorectal screening recommendations

### Knowledge Base Integration

- **Dynamic Citations**: Queries `MedicalSearchEngine` for relevant evidence
- **Fallback System**: Validated static citations when KB unavailable
- **Recommendation Pairing**: Each recommendation includes corresponding citations

### Data Flow

1. `PatientData` object provides validated input via `to_calculator_dict()`
2. Individual calculators return structured results (`FINDRISCResult`, `FraminghamResult`, `ColorectalResult`)
3. Runner integrates results into comprehensive assessment with priority actions

## Output Structure

### Individual Calculator Results

- **Risk scores/percentages** with validated thresholds
- **Evidence-based recommendations** with citations
- **Supporting evidence** from knowledge base or fallbacks
- **Next steps** and follow-up intervals

### Integrated Runner Results

- **Success metrics** and error handling per calculator
- **Priority clinical actions** with urgency levels
- **Integrated risk profile** across all domains
- **Comprehensive reporting** with patient summaries

## Important Notes

### Medical Disclaimers

All medication and therapy recommendations include **"Consult your medical provider"** for appropriate clinical oversight.

### Knowledge Base Fallbacks

If the knowledge base is unavailable, calculators automatically use validated static citations from:

- American Diabetes Association Standards of Care
- AHA/ACC Prevention Guidelines
- USPSTF Recommendations
- Diabetes Prevention Program trials

### Error Handling

- Robust validation with meaningful error messages
- Partial results returned if some calculators fail
- Age-gating handled gracefully (e.g., Framingham 30-79 years)

### Cross-Platform Compatibility

- **File Paths**: Code uses `pathlib.Path` for automatic path separator handling
- **Module Execution**: Use `python -m calculators.runner` for cross-platform compatibility
- **Direct Script Execution**: Use forward slashes (/) on Unix/Linux/macOS, backslashes (\) on Windows
- **Python Command**: May need `python3` instead of `python` on some Unix/Linux systems

## Requirements

Based on the imports and functionality found in the calculator files:

```python
# Core dependencies
sys
pathlib
typing
dataclasses
enum
datetime
math

# Components
data_models.patient_data
knowledge_base.MedicalSearchEngine (optional)

# External dependencies
# None required (knowledge base integration optional)
```

## Usage

### Running Individual Calculators

```python
from calculators import FINDRISCCalculator, ModifiedFraminghamCalculator, ColorectalScreeningCalculator
from data_models.patient_data import PatientData

# FINDRISC Example
findrisc = FINDRISCCalculator()
result = findrisc.calculate_findrisc(patient.to_calculator_dict())
print(f"Diabetes Risk: {result.risk_level.value} ({result.ten_year_risk_percentage}%)")

# Framingham Example (age 30-79)
framingham = ModifiedFraminghamCalculator()
cvd_result = framingham.calculate_framingham_risk(patient.to_calculator_dict())
print(f"CVD Risk: {cvd_result.risk_level.value} ({cvd_result.ten_year_risk_percentage}%)")

# Colorectal Example
colorectal = ColorectalScreeningCalculator()
screening_result = colorectal.assess_colorectal_screening(patient.to_calculator_dict())
print(f"Screening: {screening_result.recommendation.value}")
```

### Command Line Interface

**Comprehensive assessment**

```bash
python -m calculators.runner
```

**Individual calculator demos**

*macOS/Linux:*

```bash
python calculators/findrisc.py
python calculators/framingham.py
python calculators/colorectal.py
```

*Windows:*

```cmd
python calculators\findrisc.py
python calculators\framingham.py
python calculators\colorectal.py
```

### Package Health Check

```python
from calculators import check_calculator_health

health_status = check_calculator_health()
print(f"System Status: {health_status['status']}")
print(f"Calculators Loaded: {health_status['calculators_loaded']}")
```

## Calculator Coverage

### FINDRISC Validation

- **Risk Scoring**: Age, BMI, waist circumference, lifestyle factors validation
- **Lifestyle Assessment**: Physical activity, diet, medication history scoring
- **Family History**: Diabetes family history with proper risk weighting
- **Evidence Integration**: Dynamic citations from knowledge base with ADA/DPP fallbacks

### Modified Framingham Testing

- **Age Validation**: Proper handling of 30-79 age range with graceful degradation
- **Risk Categorization**: AHA/ACC 2018 risk thresholds (low/borderline/intermediate/high)
- **Blood Pressure**: 2017 AHA/ACC BP categories with treatment recommendations
- **Medical Disclaimers**: "Consult your medical provider" inclusion for therapy recommendations

### Colorectal Screening Assessment

- **Age-Based Logic**: USPSTF 2021 age recommendations (45-49 Grade B, 50-75 Grade A)
- **Risk Stratification**: Family history and personal risk factor evaluation
- **High-Risk Referral**: Genetic counseling recommendations for hereditary conditions
- **Screening Methods**: Colonoscopy, FIT, Cologuard interval management

## Configuration

### Version Management

```python
__version__ = "1.0.0"
__status__ = "Development - Calculators operational"
__author__ = "Selin Birinci"
```

### Knowledge Base Integration

```python
# Dynamic citation retrieval (when available)
try:
    from knowledge_base import MedicalSearchEngine
    # KB-powered evidence retrieval
except ImportError:
    # Fallback to static evidence-based citations
```

### Required Patient Data Fields

```python
# Core demographics
age, gender, height, weight  # BMI auto-calculated

# Clinical measurements
systolic_bp, diastolic_bp, total_cholesterol, hdl_cholesterol
waist_circumference

# Medical history
hypertension_medication, diabetes, smoking_status
high_glucose_history, family_diabetes_history

# Lifestyle factors
physical_activity, vegetable_fruit_daily

# Screening history
family_colorectal_history, personal_polyp_history
```

## Running Calculators

### Prerequisites

1. **Patient Data Model**: `data_models/patient_data.py` with `PatientData` class
2. **Project Structure**: Run from project root for proper imports
3. **Optional**: Weaviate knowledge base for dynamic citations

### Individual Calculator Execution

```bash
# Test FINDRISC with demo data
python calculators/findrisc.py      # Unix/Linux/macOS
python calculators\findrisc.py      # Windows

# Test Framingham with age validation
python calculators/framingham.py    # Unix/Linux/macOS
python calculators\framingham.py    # Windows

# Test colorectal screening recommendations
python calculators/colorectal.py    # Unix/Linux/macOS
python calculators\colorectal.py    # Windows
```

### Comprehensive Assessment

```bash
# Run all calculators with integrated reporting (cross-platform)
python -m calculators.runner

# Alternative execution method
python calculators/runner.py        # Unix/Linux/macOS
python calculators\runner.py        # Windows
```

### Exit Codes and Error Handling

- **Successful Assessment**: Complete results with recommendations and citations
- **Partial Success**: Some calculators succeed, others report errors with graceful degradation
- **Validation Errors**: Clear error messages for missing or invalid patient data
- **Age-Gating**: Framingham reports eligibility notes for patients outside 30-79 range

## Integration

The calculator suite validates integration between:

1. **Patient Data ↔ Calculators**: Validated input through `PatientData.to_calculator_dict()`
2. **Calculators ↔ Knowledge Base**: Dynamic evidence retrieval with `MedicalSearchEngine`
3. **Individual Results ↔ Runner**: Comprehensive assessment through `MultiCalculatorRunner`
4. **Clinical Logic ↔ Citations**: Evidence-based recommendations with peer-reviewed citations

### Knowledge Base Integration

- Dynamic citation retrieval through `search_by_calculator()` and `search_medical_content()`
- Fallback to validated static citations when KB unavailable
- Recommendation-citation pairing for clinical transparency
- Supporting evidence objects for rich clinical context

### Runner Integration

- **Priority Action Generation**: Clinical urgency assessment across all risk domains
- **Integrated Risk Profiling**: Cross-calculator risk synthesis
- **Comprehensive Reporting**: Formatted clinical summaries with patient demographics
- **Error Resilience**: Partial results when individual calculators fail

The calculator suite ensures clinical accuracy, evidence-based recommendations, and appropriate medical disclaimers across all SourceWell risk assessment components.

## Core References

1. Lindström J, Tuomilehto J. *Diabetes Care*. 2003;26(3):725-731 (FINDRISC)
2. D'Agostino RB Sr, et al. *Circulation*. 2008;117(6):743-753 (Framingham)
3. Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. *Circulation*. 2019;140(11):e596-e646
4. US Preventive Services Task Force. *JAMA*. 2021;325(19):1965-1977 (Colorectal)
5. American Diabetes Association. Standards of Medical Care in Diabetes—2024. *Diabetes Care*. 2024;47(Suppl 1):S1-S321
