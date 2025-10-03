# SourceWell Test Suite

Comprehensive testing for medical knowledge base, risk calculators, and AI integration components.

## Overview

The SourceWell Test Suite provides comprehensive validation for a healthcare AI platform focused on risk assessment and medical knowledge management. This test module ensures clinical accuracy, knowledge base integrity, and proper integration between calculators and medical content. It includes version-aware testing with smart content allocation and healthcare compliance validation.

## Features

- **Multi-Calculator Testing**: Clinical validation of FINDRISC, Modified Framingham, and Colorectal Screening calculators
- **Knowledge Base Validation**: Schema creation, content ingestion, and search functionality testing
- **Infrastructure Testing**: Weaviate connectivity, semantic search, and citation verification
- **Smart Content Requirements**: Dynamic content allocation based on available medical documents
- **Clinical Compliance**: Medical disclaimer validation and therapy recommendation testing
- **Performance Benchmarking**: Assessment timing and generation speed evaluation
- **Version Management**: Fallback version handling and healthcare audit logging

## Test Components

### Core Test Module (`__init__.py`)

- **Environment Validation**: Checks system health and content adequacy
- **Content Requirements**: Dynamic allocation based on platform version (5+ documents for development, 15+ for production)
- **Calculator Coverage**: Validates content support for required calculators
- **Full Suite Execution**: Orchestrates infrastructure, knowledge base, and calculator tests

### Calculator Tests (`test_calculators.py`)

- **TestCalculatorAccuracy**: Individual calculator validation with clinical scenarios
  - FINDRISC low/high risk scenario testing
  - Framingham BP categorization with AHA/ACC 2017 guidelines
  - Colorectal screening logic by age groups
- **TestMultiCalculatorRunner**: Integrated multi-calculator assessments
- **TestKnowledgeBaseIntegration**: Citation availability and fallback behavior
- **TestClinicalCompliance**: Medical disclaimer and therapy recommendation validation

### Knowledge Base Tests (`test_knowledge_base.py`)

- **TestMedicalKnowledgeBase**: Comprehensive knowledge base functionality
  - Weaviate connectivity and schema validation
  - Search functionality across MedicalGuideline and ResearchAbstract collections
  - Calculator-specific content filtering
  - Citation integrity verification

### Infrastructure Tests (`infrastructure_test.py`)

- **Weaviate Connection**: Basic connectivity and collection existence
- **Content Counts**: Medical content ingestion verification
- **Semantic Search**: Medical query processing with near_text functionality
- **Calculator Metadata**: Validation of calculator_support properties
- **Citation Format**: Proper citation formatting with required elements

### Search Demonstration (`search_demo.py`)

- **Interactive Search Demo**: Predefined queries for calculator-relevant content
- **Calculator-Specific Filtering**: Content discovery by calculator type
- **Knowledge Base Statistics**: Document counts and search result display

### System Testing (`test_full_system.py`)

- **Comprehensive System Validation**: Full platform testing including AI engine
- **Performance Benchmarking**: Generation speed and model loading tests
- **Integration Testing**: Calculator → AI pipeline validation

## Requirements

Based on the imports and functionality found in the test files:

```python
# Core dependencies
sys
unittest
time
logging
pathlib
typing
packaging.version

# Components
knowledge_base
calculators
data_models.patient_data
# AI engine components (specific modules may vary)

# External dependencies
weaviate
torch (for AI engine tests)
```

## Usage

### Running the Full Test Suite

```python
from tests import run_full_suite

# Run comprehensive test suite
results = run_full_suite(verbose=True)
print(f"Success: {results['overall_success']}")
```

### Command Line Interface

```bash
# Run full test suite
python -m tests

# Run specific test components
python tests/test_calculators.py
python tests/test_knowledge_base.py
python tests/infrastructure_test.py
```

### Environment Validation

```python
from tests import validate_environment, validate_content_adequacy

# Check system readiness
env_status = validate_environment()
print(f"Ready for testing: {env_status['ready_for_testing']}")

# Check content adequacy
content_status = validate_content_adequacy()
print(f"Sufficient content: {content_status['sufficient_content']}")
```

## Test Coverage

### Calculator Validation

- **FINDRISC Calculator**: Low-risk (≤7 points) and high-risk (≥15 points) scenarios
- **Modified Framingham**: Blood pressure categorization, CVD risk assessment, age boundary validation (30-79 years)
- **Colorectal Screening**: Age-based recommendations, family history risk assessment

### Knowledge Base Testing

- **Schema Validation**: MedicalGuideline and ResearchAbstract collection setup
- **Search Functionality**: Semantic search and content filtering capabilities
- **Content Requirements**: Minimum document thresholds with smart allocation
- **Citation Integrity**: Required elements validation (DOI, PMID, "Available from")

### Clinical Scenarios

Test scenarios include validated patient data:

- Low-risk young female patients
- High-risk middle-aged male patients with multiple risk factors
- Elderly patients (outside Framingham age range)
- Patients with family history considerations

### Performance Testing

- Assessment completion within 15 seconds
- AI generation speed benchmarking
- Model loading time evaluation

## Configuration

### Version Management

```python
FALLBACK_VERSION = "0.1.0"
FALLBACK_STATUS = "Development-Fallback"

# Dynamic content requirements by version
# Development: 5 total documents (3 guidelines, 2+ abstracts)
# Production v1.0+: 15 total documents (8 guidelines, 7+ abstracts)
```

### Required Calculators

```python
REQUIRED_CALCULATORS = ["FINDRISC", "ModifiedFramingham", "ColorectalScreening"]
```

### Content Adequacy Thresholds

- Minimum 2 calculators must have supporting content
- Smart allocation balances guidelines and research abstracts
- Calculator-specific metadata validation

## Running Tests

### Prerequisites

1. Weaviate running: `docker-compose up -d`
2. Content ingested: `python knowledge_base/content_ingester.py`
3. Required collections: MedicalGuideline, ResearchAbstract

### Test Execution

```bash
# Infrastructure validation
python tests/infrastructure_test.py

# Knowledge base testing
python tests/test_knowledge_base.py

# Calculator validation
python tests/test_calculators.py

# Interactive search demo
python tests/search_demo.py

# Complete system test
python tests/test_full_system.py
```

### Exit Codes

- `0`: All tests passed
- `1`: Some tests failed
- `2`: Test execution error

## Integration

The test suite validates integration between:

1. **Knowledge Base ↔ Calculators**: Content discovery by calculator type using `search_by_calculator()`
2. **Calculators ↔ AI Engine**: Risk assessment result processing and explanation generation
3. **Medical Content ↔ Citations**: Fallback citation availability when knowledge base is unavailable
4. **Version Management ↔ Requirements**: Dynamic content thresholds based on platform version

### Knowledge Base Integration

- Tests `MedicalSearchEngine` with calculator-specific filtering
- Validates `calculator_support` metadata across medical guidelines
- Ensures citation availability through knowledge base or fallback mechanisms

### Calculator Integration

- Multi-calculator assessment through `MultiCalculatorRunner`
- Patient data validation with `PatientData.validate()`
- Priority action generation for high-risk patients
- Medical disclaimer inclusion in therapy recommendations

The test suite ensures clinical accuracy, system reliability, and healthcare compliance across all SourceWell components.
