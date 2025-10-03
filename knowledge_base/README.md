# Medical Knowledge Base Module

A comprehensive medical content management system with semantic search capabilities, citation verification, and healthcare-compliant data handling for evidence-based clinical decision support.

## Overview

The Medical Knowledge Base Module provides a robust foundation for managing clinical guidelines and research abstracts with full citation tracking, semantic search capabilities, and integration support for medical risk calculators. Built on Weaviate vector database, it ensures high-quality medical content through mandatory validation and provides AI-ready semantic search for clinical applications.

### Key Features

- **Medical Content Ingestion**: Process clinical guidelines and research abstracts from Markdown files with YAML frontmatter
- **Citation Management**: Automatic Vancouver-style citation generation with complete bibliographic metadata
- **Semantic Search**: AI-powered content discovery with calculator-specific filtering
- **Content Validation**: Mandatory approval workflow with comprehensive error reporting
- **Duplicate Prevention**: SHA256-based content hashing prevents data duplication
- **Basic Audit Trails**: Content ingestion tracking and validation workflows

## Architecture

```
Medical Knowledge Base Module
├── schema_setup.py          # Weaviate collection management
├── content_ingester.py      # Medical content processing
├── search_engine.py         # Semantic search interface
├── config.py               # System configuration
└── __init__.py            # Module API and health checks

Data Flow:
Markdown Files → Validation → Citation Generation → Weaviate Storage → Semantic Search
```

### Supported Content Types

- **Medical Guidelines**: Clinical practice guidelines from organizations (ADA, ACC/AHA, USPSTF)
- **Research Abstracts**: Peer-reviewed medical research with PubMed integration
- **Risk Calculators**: FINDRISC, Modified Framingham, Colorectal Screening support

## Installation

### Prerequisites

- Python 3.8+
- Docker (for Weaviate)
- 4GB+ available RAM

### System Dependencies

**macOS/Linux:**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker --version
```

**Windows:**

```cmd
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
# Follow installation wizard
docker --version
```

### Python Dependencies

```bash
pip install weaviate-client PyYAML
```

### Weaviate Setup

**macOS/Linux:**

```bash
# Start Weaviate with Docker
docker run -d \
  --name weaviate \
  -p 8080:8080 \
  -p 50051:50051 \
  -e QUERY_DEFAULTS_LIMIT=25 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=none \
  -e ENABLE_MODULES=text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai \
  semitechnologies/weaviate:1.22.4

# Verify Weaviate is running
curl http://localhost:8080/v1/meta
```

**Windows (Command Prompt):**

```cmd
docker run -d ^
  --name weaviate ^
  -p 8080:8080 ^
  -p 50051:50051 ^
  -e QUERY_DEFAULTS_LIMIT=25 ^
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true ^
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate ^
  -e DEFAULT_VECTORIZER_MODULE=none ^
  -e ENABLE_MODULES=text2vec-openai,text2vec-cohere,text2vec-huggingface,ref2vec-centroid,generative-openai,qna-openai ^
  semitechnologies/weaviate:1.22.4

curl http://localhost:8080/v1/meta
```

## Quick Start

### 1. Initialize Database Schema

```bash
python -m knowledge_base.schema_setup setup
```

### 2. Prepare Medical Content

Create directory structure:

```
data/
└── medical_content/
    ├── guidelines/
    │   └── ada_diabetes_2023.md
    └── research_abstracts/
        └── diabetes_risk_study.md
```

### 3. Medical Content Format

**Clinical Guideline Example:**

```markdown
---
content_type: MedicalGuideline
review_status: approved
organization: American Diabetes Association
title: Standards of Medical Care in Diabetes
section: Risk Assessment
page_reference: "15-18"
publication_year: 2023
url: https://diabetesjournals.org/care/issue/46/Supplement_1
accessed_date: "2023-12-01"
evidence_grade: "A"
calculator_support: ["FINDRISC", "ModifiedFramingham"]
medical_domain: ["Endocrinology", "Primary Care"]
---

# Diabetes Risk Assessment and Screening

Diabetes risk assessment should include validated risk calculators such as FINDRISC for identifying individuals at high risk for type 2 diabetes. The assessment should consider family history, BMI, age, and lifestyle factors.
Adults aged 35 years and older should be screened for diabetes and prediabetes. Screening should be considered for adults younger than 35 years who are overweight or obese and have one or more additional risk factors for diabetes.
The FINDRISC (Finnish Diabetes Risk Score) provides a simple, noninvasive, and inexpensive screening tool for identifying individuals at high risk for type 2 diabetes. A FINDRISC score ≥15 indicates high risk and warrants further diagnostic testing.

**Calculator Integration:**
- FINDRISC score calculation considers age, BMI, waist circumference, physical activity, vegetable consumption, hypertension medication, history of high glucose, and family history of diabetes
- Modified Framingham Risk Score may be used in conjunction for cardiovascular risk assessment in diabetic patients
- Integration with electronic health records enables automated risk stratification during routine clinical encounters
```

**Research Abstract Example:**

```markdown
---
content_type: ResearchAbstract
review_status: approved
title: Validation of FINDRISC Score in Primary Care Settings
authors: ["Smith J", "Johnson A", "Williams B"]
journal: Diabetes Care
publication_year: 2023
pmid: "12345678"
doi: "10.2337/dc23-0001"
study_type: "Validation Study"
population_size: 2847
evidence_level: "Level II"
calculator_support: ["FINDRISC"]
medical_domain: ["Primary Care", "Endocrinology"]
accessed_date: "2023-12-01"
---

# Validation of FINDRISC Score in Primary Care Settings: A Multicenter Prospective Study

**Background:**
The Finnish Diabetes Risk Score (FINDRISC) was originally developed and validated in Finnish populations, but its performance in diverse primary care settings remains unclear. This study aimed to validate the FINDRISC score for identifying undiagnosed type 2 diabetes and prediabetes in a multicenter primary care population.
We conducted a prospective validation study across 12 primary care clinics, enrolling 2,847 adults aged 18-75 years without known diabetes. Participants completed the FINDRISC questionnaire and underwent oral glucose tolerance testing (OGTT) as the reference standard. We calculated sensitivity, specificity, and area under the receiver operating characteristic curve (AUC) for various FINDRISC cutoff points.

**Key Findings:**
This validation study assessed the performance of the FINDRISC score in identifying diabetes risk among 2,847 primary care patients. The study found high sensitivity (87%) and specificity (79%) for detecting undiagnosed diabetes using a cutoff score of ≥15. The AUC was 0.85 (95% CI: 0.82-0.88) for detecting type 2 diabetes and 0.78 (95% CI: 0.75-0.81) for detecting prediabetes.
The FINDRISC score demonstrated excellent performance for identifying undiagnosed type 2 diabetes in primary care settings. A cutoff score of ≥15 provides optimal balance between sensitivity and specificity, making it suitable for clinical implementation as a screening tool.

**Calculator Integration:**
- FINDRISC score ≥15 showed 87% sensitivity and 79% specificity for diabetes detection
- Electronic health record integration enabled automated risk scoring during routine visits
- Cost-effectiveness analysis demonstrated significant healthcare savings through early identification and prevention
- Implementation in clinical decision support systems improved screening rates by 34% across participating practices
```

### 4. Ingest Content

```bash
python -m knowledge_base.content_ingester
```

### 5. Search Medical Content

```python
from knowledge_base import MedicalSearchEngine

with MedicalSearchEngine() as search:
    # Semantic search
    results = search.search_medical_content(
        query="diabetes risk assessment tools",
        limit=5
    )
  
    # Calculator-specific search
    findrisc_content = search.search_by_calculator("FINDRISC")
  
    for result in results:
        print(f"Title: {result.title}")
        print(f"Citation: {result.citation}")
        print(f"Calculators: {result.calculator_support}")
```

## Configuration

### Environment Variables

```bash
# Weaviate connection settings
export WEAVIATE_HTTP_PORT=8080
export WEAVIATE_GRPC_PORT=50051
```

**Windows:**

```cmd
set WEAVIATE_HTTP_PORT=8080
set WEAVIATE_GRPC_PORT=50051
```

### Supported Risk Calculators

- `FINDRISC`: Finnish Diabetes Risk Score
- `ModifiedFramingham`: Modified Framingham Risk Score
- `ColorectalScreening`: Colorectal Cancer Screening Risk

## API Reference

### System Health and Information

```python
from knowledge_base import get_system_info, check_system_health

# Get system statistics
info = get_system_info()
print(f"Version: {info['version_info']['platform_version']}")
print(f"Total Documents: {info['total_documents']}")

# Perform health check
health = check_system_health()
print(f"System Operational: {health['operational']}")
if health['issues']:
    print(f"Issues: {', '.join(health['issues'])}")
```

### Schema Management

```python
from knowledge_base import MedicalSchemaManager

with MedicalSchemaManager() as schema:
    # Setup complete schema
    success = schema.setup_complete_schema()
  
    # Check connection
    connected = schema.check_weaviate_connection()
  
    # Get existing collections
    collections = schema.get_existing_collections()
```

### Content Ingestion

```python
from knowledge_base import MedicalContentIngester

ingester = MedicalContentIngester()
try:
    # Ingest all approved content
    stats = ingester.ingest_all_approved_content()
    print(f"Successfully ingested: {stats['successfully_ingested']} documents")
  
    # Check ingestion status
    state = ingester.load_ingestion_state()
  
finally:
    ingester.close()
```

### Search Operations

```python
from knowledge_base import MedicalSearchEngine

with MedicalSearchEngine() as search:
    # Get knowledge base statistics
    stats = search.get_knowledge_base_stats()
  
    # Semantic search with filtering
    results = search.search_medical_content(
        query="cardiovascular risk assessment",
        content_type="MedicalGuideline",
        calculator_filter="ModifiedFramingham",
        limit=10,
        search_method="semantic"
    )
  
    # Process search results
    for result in results:
        print(f"Title: {result.title}")
        print(f"Organization: {result.organization}")
        print(f"Citation: {result.citation}")
        print(f"Evidence Grade: {result.evidence_grade}")
```

## Command Line Interface

### Schema Management

```bash
# Setup database schema
python -m knowledge_base.schema_setup setup

# Check Weaviate connection
python -m knowledge_base.schema_setup check

# Reset schema (destructive)
python -m knowledge_base.schema_setup reset
```

### Content Ingestion

```bash
# Ingest all approved content
python -m knowledge_base.content_ingester

# Check ingestion status
python -m knowledge_base.content_ingester status

# Reset ingestion state
python -m knowledge_base.content_ingester reset
```

### Search Testing

```bash
# Test semantic search
python -m knowledge_base.search_engine "diabetes risk factors"
```## Data Validation Requirements

### Required Fields (All Content Types)

- `content_type`: "MedicalGuideline" or "ResearchAbstract"
- `review_status`: Must be "approved" for ingestion
- `publication_year`: Integer year
- `calculator_support`: Array of supported calculator names
- `medical_domain`: Array of medical specialties
- `accessed_date`: ISO date format "YYYY-MM-DD"

### Medical Guidelines

- `organization`: Publishing organization name
- `title`: Document title
- `section`: Section reference
- `url`: Source URL

### Research Abstracts

- `title`: Research paper title
- `journal`: Journal name
- `authors`: Array of author names
- Optional: `pmid`, `doi`, `study_type`, `population_size`

## Troubleshooting

### Common Issues

**Weaviate Connection Failed**

```bash
# Check if Weaviate is running
docker ps | grep weaviate

# Check connectivity
curl http://localhost:8080/v1/meta

# Restart Weaviate
docker restart weaviate
```

**Content Not Ingesting**

1. Verify `review_status: approved` in YAML frontmatter
2. Check validation error logs in `data/medical_content/processed/validation_reports/`
3. Ensure required fields are present

**Search Returns No Results**

1. Verify content ingestion completed successfully
2. Check knowledge base statistics: `python -m knowledge_base.search_engine`
3. Confirm Weaviate vector indexing is complete

### Log Analysis

**macOS/Linux:**

```bash
# View recent logs
tail -f data/medical_content/processed/validation_reports/*.log

# Check ingestion state
cat data/medical_content/processed/validation_reports/ingestion_state.json | python -m json.tool
```

**Windows:**

```cmd
type data\medical_content\processed\validation_reports\*.log

python -m json.tool data\medical_content\processed\validation_reports\ingestion_state.json
```

## Development Guidelines

### Adding New Content Types

1. Update `config.py` with new content type constants
2. Modify schema in `schema_setup.py`
3. Add validation rules in `content_ingester.py`
4. Update citation generation logic
5. Extend search result handling

### Testing Content Validation

```python
from knowledge_base import MedicalContentIngester
from pathlib import Path

ingester = MedicalContentIngester()
metadata = ingester.parse_markdown_file(Path("test_content.md"))
is_valid, errors = ingester.validate_metadata(metadata, Path("test_content.md"))

if not is_valid:
    print("Validation errors:", errors)
```

### Custom Citation Formats

Extend the `generate_vancouver_citation` method in `MedicalContentIngester` for additional citation styles or content types.

## Version Information

Current version: 0.1.0 (Development-Fallback)

- Weaviate v4 API compatibility
- Vancouver citation standard
- Basic audit trails and content validation
- Semantic search with vector embeddings

## License and Compliance

This module provides foundational features for healthcare applications including content validation workflows, ingestion audit trails, and version tracking. While designed with healthcare use cases in mind, **additional security, privacy, and compliance controls must be implemented** for production healthcare environments.

### Current Compliance Features:

- Content validation and approval workflows
- Ingestion audit trails with timestamp logging
- Version tracking and duplicate prevention
- Error reporting and validation logs

### Additional Requirements for Healthcare Production:

- Implement appropriate data governance policies
- Add user authentication and authorization controls
- Ensure HIPAA/HITECH compliance for PHI handling
- Implement data encryption and secure transmission
- Add comprehensive audit logging for all system access
- Establish data retention and deletion policies

**Important**: This module handles medical literature and guidelines, not patient data (PHI). Ensure proper compliance assessment before production deployment.