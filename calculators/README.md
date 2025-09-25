# SourceWell Risk Calculator Suite
# Risk Assessment Calculators (FINDRISC, Framingham, Colorectal)   

Evidence-based preventive health risk calculators with mandatory citation verification and knowledge base (KB) integration.

This folder provides:

- **FINDRISC** (diabetes) risk scoring with evidence-backed recommendations
- **Modified Framingham** (cardiovascular) 10-year risk estimation with guideline-driven therapy prompts
- **USPSTF 2021** colorectal cancer screening recommendations with risk stratification
- **A Multi-Calculator Runner** that orchestrates all calculators into one comprehensive assessment

All recommendations are citation-verified via the Knowledge Base, with robust evidence fallbacks if the KB is unavailable.

## Quick Start

### Prerequisites

- Python project root on `sys.path` (run from project root)
- Patient data model available: `data_models/patient_data.py`
- Optional (recommended): Weaviate KB running (`docker-compose up -d`) for dynamic citations

### Run the comprehensive demo (preferred)

**Module execution:**

```bash
# Windows/macOS/Linux
python -m calculators.runner
```

**Direct script execution:**

```bash
python calculators/runner.py
```

### Run individual calculators (demos)

```bash
# FINDRISC
python calculators/findrisc.py

# Framingham
python calculators/framingham.py

# Colorectal
python calculators/colorectal.py
```

### Package import example (programmatic)

```python
from calculators import MultiCalculatorRunner
from data_models.patient_data import PatientData, get_test_scenarios

runner = MultiCalculatorRunner()
patient = PatientData.from_dict(get_test_scenarios()['high_risk_middle_aged_male'])
results = runner.run_all_assessments(patient)
runner.print_comprehensive_report(results)
```

### Health check

```python
from calculators import check_calculator_health
print(check_calculator_health())
```

## Clinical Overview (Calculator-by-Calculator)

All calculators implement evidence-based logic with citations from tier-1 sources. When medication or device therapy is suggested, user-facing text includes **"Consult your medical provider."**

### FINDRISC - Finnish Diabetes Risk Score

*Lindström & Tuomilehto, Diabetes Care 2003*

**Inputs:** age, gender, BMI (auto-calculated from PatientData), waist circumference, physical activity, fruit/vegetable intake, hypertension medication, prior high glucose, family diabetes history

**Scoring thresholds (total 0–26):**

- `0–7`: Low (~1%)
- `8–11`: Slightly elevated (~4%)
- `12–14`: Moderate (~17%)
- `15–20`: High (~33%)
- `21–26`: Very high (~50%)

**Evidence-based outputs:**

- Screening intervals and test recommendations (HbA1c, fasting glucose)
- Diabetes prevention program evidence (DPP)
- Lifestyle targets (weight reduction, physical activity, fiber intake)

**Citations:** ADA Standards of Care, DPP trial, FINDRISC validation; KB dynamic citations when available

### Modified Framingham 10-Year CVD Risk

*D'Agostino et al., Circulation 2008; AHA/ACC guidance*

**Inputs:** age (30–79), gender, total cholesterol, HDL, systolic/diastolic BP, BP meds, smoking status, diabetes

**Risk categories (2018 AHA/ACC):**

- `<5%`: Low
- `5–7.4%`: Borderline
- `7.5–19.9%`: Intermediate
- `≥20%`: High

**Evidence-based outputs:**

- Statin therapy intensity (*"Consult your medical provider."*)
- Blood pressure targets and therapy (*"Consult your medical provider."*)
- Smoking cessation support
- Diabetes agents with CV benefit (SGLT2/GLP-1) (*"Consult your medical provider."*)
- Lifestyle (Mediterranean diet, 150 min/week exercise)

**Citations:** AHA/ACC 2017 BP, 2019 Primary Prevention, ADA Standards; KB dynamic citations when available

### Colorectal Cancer Screening (USPSTF 2021)

**Inputs:** age, gender, first-degree family history & relative age at diagnosis, personal polyp history, IBD, hereditary risk, previous screening date/method

**Recommendations:**

- `<45`: Not recommended unless increased/high risk (early family history → consider starting at 40 or 10 years before relative diagnosis)
- `45–49`: Start now (Grade B)
- `50–75`: Start now (Grade A)
- `76–85`: Individualize decision (Grade C)
- `≥85`: Not recommended (Grade D)

**Methods & intervals:** Colonoscopy q10y, FIT yearly, Cologuard q3y (sigmoidoscopy optional)

**High-risk/IBD/hereditary:** Gastroenterology referral (specialized schedule)

**Citations:** USPSTF 2021, ACS 2018, NCCN; KB dynamic citations when available

### Clinical disclaimer

Where therapy is suggested (statins, antihypertensives, diabetes medications, nicotine replacement, aspirin), user-facing strings include **"Consult your medical provider."**

## Technical Architecture

### Modules

- `calculators/findrisc.py` – FINDRISC calculator (evidence-based recommendation generation with KB + fallbacks)
- `calculators/framingham.py` – Modified Framingham risk with AHA/ACC evidence-based recommendations (+ disclaimers)
- `calculators/colorectal.py` – USPSTF 2021 screening logic with risk stratification and intervals
- `calculators/runner.py` – Orchestrates all calculators, integrates results, generates priority actions and integrated risk profiles
- `calculators/__init__.py` – Clean package interface (exports calculators and runner) + `check_calculator_health()`

### Knowledge base integration

- **Dynamic citations:** All calculators query the KB via `MedicalSearchEngine` for relevant guideline/research passages and use their citations
- **Fallback behavior:** If KB is unavailable, calculators provide validated static citations from peer-reviewed or major guideline sources
- **Mandatory citation policy:** Each recommendation list is paired with `recommendation_citations`; each calculator also returns general `evidence_citations`

### Data flow

1. Patient data is collected separately via `data_models.PatientData`
2. `patient.to_calculator_dict()` produces a clean dict with validated fields and aliases for calculators
3. Each calculator returns a structured dataclass (`FINDRISCResult`, `FraminghamResult`, `ColorectalResult`)
4. Runner combines outputs and produces:
   - Integrated risk profile (diabetes/CVD/screening)
   - Priority clinical actions list with sensible escalation

### Error handling

- Robust type checks and try/except paths ensure partial results are still returned
- If one calculator fails, others continue; the runner reports errors per domain
- Age-gating (e.g., Framingham 30–79) handled gracefully with eligibility notes

### Import & execution strategy

- All modules add the project root to `sys.path` at runtime for direct execution
- Runner supports both absolute and relative imports (auto-detects)
- **Preferred execution:** `python -m calculators.runner`

### Performance

- Knowledge base calls are limited per decision point (limit=1–3)
- Duplicate recommendations/citations are de-duplicated while preserving order

## How to Use (Developers)

### Typical programmatic usage

```python
from calculators import MultiCalculatorRunner
from data_models.patient_data import PatientData, get_test_scenarios

runner = MultiCalculatorRunner()
patient = PatientData.from_dict(get_test_scenarios()['high_risk_middle_aged_male'])
results = runner.run_all_assessments(patient)
runner.print_comprehensive_report(results)
```

### Using individual calculators

```python
from calculators import FINDRISCCalculator

calc = FINDRISCCalculator()
result = calc.calculate_findrisc(patient.to_calculator_dict())
print(result.recommendations)
print(result.recommendation_citations)
```

### Package health

```python
from calculators import check_calculator_health
print(check_calculator_health())
```

### Command-line demos

```bash
python calculators/findrisc.py
python calculators/framingham.py
python calculators/colorectal.py
python -m calculators.runner
```

## Inputs & Validation

### Expected input source

- `data_models.PatientData` handles validation, normalization, and BMI auto-calculation
- Use `PatientData.from_dict()` and `patient.validate()` before running calculators

### Key validation rules (high-level)

- **Age:** FINDRISC (adult, practical use), Framingham (30–79), USPSTF screening (focus ≥45 unless increased risk)
- **Clinical plausibility ranges** enforced by PatientData (BP, cholesterol, BMI derived from height/weight)
- **Inter-field logic** (e.g., `family_colorectal_age` required when family history is positive)

## Output Structure (Highlights)

### FINDRISCResult

- `total_score`, `risk_level`, `ten_year_risk_percentage`, `risk_description`
- `recommendations`, `recommendation_citations`
- `evidence_citations`, `supporting_evidence`

### FraminghamResult

- `ten_year_risk_percentage`, `risk_level`, `risk_description`
- `bp_category`
- `recommendations`, `recommendation_citations`
- `evidence_citations`, `supporting_evidence`

### ColorectalResult

- `recommendation` (`START_NOW`, `CONTINUE`, `DISCUSS`, `NOT_RECOMMENDED`, `HIGH_RISK_REFERRAL`)
- `recommended_methods`, `screening_interval`
- `risk_level`, `rationale`, `next_screening_date`
- `recommendations`, `recommendation_citations`
- `evidence_citations`, `supporting_evidence`

### Runner results

- `success`, `patient_summary`, `clinical_summary`, `assessment_date`
- `results`: dict with domain results or error structures
- `integrated_risk_profile`, `priority_actions`
- `calculators_run`, `successful_assessments`

## Evidence & Citations

- **Dynamic retrieval:** Knowledge Base (Weaviate) via `MedicalSearchEngine` (calculator-specific and general evidence)
- **Fallbacks:** ADA Standards of Care, AHA/ACC 2017/2019 guidelines, USPSTF 2021, DPP trial, D'Agostino 2008, ACS/NCCN for colorectal
- Every recommendation list includes matching `recommendation_citations`; calculators also return `evidence_citations` summarizing source material used

## Safety & Compliance

- Medication/device recommendations include **"Consult your medical provider."**
- The system is clinical decision support, not a substitute for medical judgment
- All content must be validated through KB or established guidelines (fallbacks)

## Tips & Gotchas

- If you see "Knowledge base unavailable," the system is using validated fallback citations—this is expected if Weaviate isn't running
- Prefer running as a module for clean imports: `python -m calculators.runner`
- Ensure `PatientData` validation passes before running assessments to avoid cascading errors
- If adding new calculators, follow the same KB-first, fallback-second citation pattern and update `calculators/__init__.py` exports

## References (Core)

1. Lindström J, Tuomilehto J. *Diabetes Care*. 2003;26(3):725–731 (FINDRISC)
2. D'Agostino RB Sr, et al. *Circulation*. 2008;117(6):743–753 (Framingham general CVD risk)
3. Whelton PK, et al. 2017 AHA/ACC BP Guideline. *Circulation*. 2018;138(17):e484–e594
4. Arnett DK, et al. 2019 AHA/ACC Primary Prevention Guideline. *Circulation*. 2019;140(11):e596–e646
5. US Preventive Services Task Force. *JAMA*. 2021;325(19):1965–1977 (Colorectal screening)
6. American Diabetes Association. Standards of Medical Care in Diabetes—2024. *Diabetes Care*. 2024;47(Suppl 1):S1–S321
7. Diabetes Prevention Program Research Group. *N Engl J Med*. 2002;346(6):393–403

---

**Version:** 1.0.0
**Status:** Development – Calculators operational
**Author:** Selin Birinci