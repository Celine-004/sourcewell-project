# Patient Data Model - Clinical Validation Documentation

## Overview

The Patient Data Model provides evidence-based clinical validation for adult preventive healthcare risk assessment. This module serves as the central data management system for FINDRISC diabetes risk, Modified Framingham cardiovascular risk, and USPSTF colorectal screening assessments.

## Key Features

- **WHO BMI Categorization:** Clinical classification (Normal Weight, Overweight, Obese Class I/II/III)
- **Evidence-Based Validation:** Clinical guardrails based on established medical literature
- **Biological Plausibility Focus:** Ranges prevent impossible entries without rejecting legitimate patients
- **Clean Architecture:** Modular design
- **Error Prevention:** Catches common unit conversion mistakes and data entry errors

## Implementation Notes

### Automatic Data Processing
- **BMI Calculation**: Computed from height_cm and weight_kg using standard formula
- **Data Normalization**: Gender lowercased, family history mapped to canonical values
- **Type Coercion**: Numeric fields accept string inputs and convert appropriately

### Inter-field Validation Rules
- If `family_colorectal_cancer = True`, then `family_colorectal_age` is required (20-100 years)
- If `family_colorectal_cancer = False`, then `family_colorectal_age` is ignored
- `previous_screening_date` must follow YYYY-MM-DD format when provided

### Calculator Integration
```python
# Clean export for risk calculators
patient = PatientData(age=52, gender='male', height_cm=175, weight_kg=95)
calculator_input = patient.to_calculator_dict()
# Provides all required fields with appropriate aliases
```
**Developer Usage:**
```python
# Using predefined test scenarios for development
from data_models.patient_data import get_test_scenarios
patient = PatientData.from_dict(scenarios['high_risk_middle_aged_male'])
calculator_input = patient.to_calculator_dict()
```

## Design Philosophy

### Validation Strategy
The validation ranges follow three core principles:

1. **Biological Plausibility Over Normality** - Ranges represent possibility, not health ideals
2. **Layered Validation Architecture** - Base validation for data quality, calculator-specific requirements, clinical interpretation  
3. **Adult Preventive Care Focus** - Optimized for USPSTF, AHA/ACC, ADA, WHO guidelines

## Clinical Validation Boundaries

| Parameter | Range/Values | Clinical Rationale | Evidence Base |
|-----------|--------------|-------------------|---------------|
| **Age** | 18-100 years | Adult preventive care scope; accommodates centenarians | USPSTF recommendations, Medicare eligibility |
| **Gender** | 'male', 'female' | Calculator requirements use binary classifications | FINDRISC, Framingham validation studies |
| **Height** | 100-250 cm | Severe dwarfism to extreme gigantism; prevents unit errors | WHO growth standards |
| **Weight** | 30-300 kg | Severe malnutrition to extreme obesity; catches lb/kg confusion | DSM-5 criteria, bariatric standards |
| **BMI** | 12.0-60.0 kg/m² | Below 12.0 = severe anorexia; above 60.0 = immediate intervention | WHO classifications, DSM-5 |
| **Waist Circumference** | 40-200 cm | Metabolic risk assessment range | IDF Metabolic Syndrome criteria |
| **Systolic BP** | 70-250 mmHg | Severe hypotension to hypertensive crisis | 2017 AHA/ACC Guidelines |
| **Diastolic BP** | 40-150 mmHg | Severe hypotension to hypertensive emergency | 2017 AHA/ACC Guidelines |
| **Total Cholesterol** | 100-500 mg/dL | Malabsorption/liver disease to familial hypercholesterolemia | NCEP ATP III Guidelines |
| **HDL Cholesterol** | 15-100 mg/dL | Tangier disease to rare very high protective levels | Framingham Heart Study |
| **Family Diabetes History** | Categorical | FINDRISC-specific categories with risk gradation | Lindström & Tuomilehto 2003 |
| **Family Colorectal Age** | 20-100 years | Early hereditary syndromes to late sporadic cases | USPSTF 2021, NCCN Guidelines |

## Family Colorectal Cancer Age - Detailed Clinical Rationale

The age at which a first-degree relative was diagnosed with colorectal cancer directly impacts screening recommendations:

### Age-Based Screening Implications

| Family Age at Diagnosis | Clinical Significance | Screening Impact |
|------------------------|----------------------|------------------|
| **20-49 years** | Strongly suggests hereditary syndrome (Lynch, FAP) | Start screening at age 40 or 10 years before family age |
| **50-59 years** | Early-onset, increased genetic risk | Consider screening at age 45 instead of 50 |
| **60+ years** | Typical sporadic colorectal cancer | Standard screening recommendations apply |

### Boundary Justification
- **Lower Bound (20 years):** Accommodates extremely rare early-onset cases indicating hereditary cancer syndromes
- **Upper Bound (100 years):** Allows centenarian diagnoses while preventing data entry errors
- **Clinical Context:** Per USPSTF 2021 guidelines, family diagnosis age determines individual screening intensity and timing

## WHO BMI Categories

| BMI Range (kg/m²) | Category | Clinical Significance |
|-------------------|----------|----------------------|
| <16.0 | Severe Underweight | Requires immediate nutritional intervention |
| 16.0-18.5 | Underweight | May indicate malnutrition or eating disorders |
| 18.5-25.0 | Normal Weight | Optimal range for health outcomes |
| 25.0-30.0 | Overweight | Increased risk for diabetes, cardiovascular disease |
| 30.0-35.0 | Obese Class I | Moderate obesity requiring lifestyle intervention |
| 35.0-40.0 | Obese Class II | Severe obesity, consider bariatric evaluation |
| ≥40.0 | Obese Class III | Extreme obesity requiring specialized care |

## Evidence-Based Methodology

Each validation boundary was established through systematic analysis:

*   **Literature Review** - Analysis of clinical guidelines and validation studies
*   **Real-World Data Analysis** - EHR ranges and population health databases
*   **Calculator Requirements** - Specific needs for risk assessment algorithms
*   **Edge Case Consideration** - Rare but medically documented conditions

## Clinical Evidence References

### Primary Guidelines

*   **World Health Organization** - BMI Classification, Global Health Observatory
*   **Whelton PK, et al.** - 2017 AHA/ACC High Blood Pressure Guidelines. *Circulation.* 2018;138(17):e484-e594
*   **US Preventive Services Task Force** - Colorectal Cancer Screening. *JAMA.* 2021;325(19):1965-1977
*   **Lindström J, Tuomilehto J** - FINDRISC diabetes risk score. *Diabetes Care.* 2003;26(3):725-731
*   **D'Agostino RB Sr, et al.** - Framingham cardiovascular risk profile. *Circulation.* 2008;117(6):743-753

### Laboratory Standards

*   **National Cholesterol Education Program (NCEP)** - ATP III Guidelines. *Circulation.* 2002;106(25):3143-3421
*   **International Diabetes Federation** - Metabolic Syndrome Definition. 2006
*   **Clinical Laboratory Standards Institute** - Reference Intervals. CLSI C28-A3c. 2010

### Healthcare Informatics

*   **HL7 FHIR R4** - Vital Signs Profiles and Observation Resources
*   **European Society of Cardiology** - Hypertension Guidelines. *European Heart Journal.* 2018