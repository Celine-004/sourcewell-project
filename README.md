# SourceWell Project

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://www.docker.com/)

> Evidence-based preventive health guidance platform combining validated clinical risk calculators with AI-powered explanations and mandatory citation verification.

## Problem Statement & Solution

### The Challenge

Individuals often receive generalized health advice that doesn't account for their unique personal and family medical history. This leads to missed prevention opportunities, reduced engagement with healthcare recommendations, and a lack of trust in AI-generated insights due to opacity.

### Our Approach

SourceWell implements a hybrid intelligent system that:

- **Collects Patient Health Data**: Comprehensive data collection with clinical validation
- **Executes Validated Risk Calculations**: Utilizes established medical formulas (FINDRISC, Modified Framingham, Colorectal screening)
- **Retrieves Relevant Medical Evidence**: Employs semantic search on a curated knowledge base
- **Generates Personalized Explanations**: Provides AI-powered insights with local LLM inference
- **Enforces Mandatory Citation Verification**: Ensures every medical claim is traceable to its source
- **Provides Evidence-Based Recommendations**: Clinical guidelines with peer-reviewed citations

## Key Innovation: Mandatory Citation Verification

**Core Differentiator**: SourceWell automatically verifies that every medical claim presented to users is directly supported by passages from curated, peer-reviewed medical sources. Any claim without verifiable evidence is either removed or flagged, ensuring unprecedented accuracy, transparency, and trustworthiness in AI-generated health guidance.

## System Architecture

```
SourceWell Platform
├── Frontend (Streamlit)           # Interactive web interface
├── Risk Calculators              # Validated clinical assessments
├── Knowledge Base (Weaviate)     # Medical literature & guidelines
├── LLM Engine (Phi-3 Mini)      # AI explanation generation
├── Citation Verifier            # Mandatory evidence verification
└── Patient Data Model           # Clinical validation system
```

The platform operates on a modular, agentic architecture that seamlessly integrates validated medical science with advanced AI capabilities, ensuring all outputs are evidence-based and clinically appropriate.

## Core Modules

### [Risk Calculator Suite](calculators/README.md)

Evidence-based preventive health risk calculators with knowledge base integration:

- **FINDRISC**: Finnish Diabetes Risk Score (10-year Type 2 diabetes risk)
- **Modified Framingham**: Cardiovascular disease risk with AHA/ACC guidelines
- **Colorectal Screening**: USPSTF 2021 cancer screening recommendations
- **Multi-Calculator Runner**: Comprehensive integrated assessment

### [Medical Knowledge Base](knowledge_base/README.md)

Comprehensive medical content management with semantic search:

- Clinical guidelines and research abstracts from Markdown files
- Vancouver-style citation generation
- Weaviate vector database with semantic search
- Calculator-specific content filtering and validation

### [LLM Engine](llm/README.md)

AI explanation system with comprehensive error handling:

- Microsoft Phi-3 Mini (4k-instruct) for local inference
- Citation verifier validates AI claims against medical sources
- Extensive error handling with text-based fallbacks
- GPU acceleration (NVIDIA/AMD) with CPU fallback support

### [Patient Data Model](data_models/README.md)

Clinical validation system for adult preventive healthcare:

- Evidence-based validation ranges based on medical literature
- Automatic BMI calculation with WHO categorization
- Biological plausibility validation (not normality)
- Clean data export for calculator integration

### [Test Suite](tests/README.md)

Comprehensive testing for clinical accuracy and system reliability:

- Multi-calculator validation
- Knowledge base integrity testing
- AI integration verification
- Healthcare compliance validation

### [Web Interface](app/README.md)

Interactive Streamlit-based healthcare risk assessment application:

- Multi-page navigation (Pacient History, Assessment, Report, Coaching)
- Interactive risk visualization with Plotly charts
- Results display with priority actions
- Session state management

## Technology Stack

### Core Technologies

- **Frontend**: Streamlit with custom CSS styling
- **AI Models**: Microsoft Phi-3 Mini (local inference), Sentence-Transformers
- **Knowledge Base**: Weaviate vector database with semantic search
- **Risk Calculators**: Custom Python implementations of validated clinical formulas
- **Platform**: Cross-platform (Windows/WSL2, macOS, Linux) with NVIDIA GPU optimization

### Key Dependencies

- **Python 3.11+** with scientific computing libraries
- **Docker Desktop** for Weaviate deployment
- **PyTorch** for AI model inference
- **Plotly** for interactive data visualization
- **Weaviate** for vector database operations

## Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Docker Desktop** installed and running
- **16GB RAM** (8GB minimum)
- **NVIDIA GPU** recommended (GTX 1060+ with 4GB VRAM)
- **15GB storage** for models and cache

### Installation

1. **Clone and Setup Environment**

```bash
git clone https://github.com/Celine-004/sourcewell-project
cd sourcewell-project

python -m venv healthcare_env
# Windows:
healthcare_env\Scripts\activate
# macOS/Linux:
# source healthcare_env/bin/activate

python setup_sourcewell.py --auto
```

2. **Start Core Services**

```bash
# Start Weaviate knowledge base
docker-compose up -d

# Initialize medical content (first run)
python -m knowledge_base.schema_setup setup
python -m knowledge_base.content_ingester
```

3. **Launch Application**

```bash
# Start web interface
streamlit run app/main.py
```

4. **Access Platform**
   - Open browser to `http://localhost:8501`
   - Complete patient data collection
   - Run comprehensive risk assessments
   - Review AI-generated insights with citations

### Quick Test

```bash
# Validate system health
python -m tests

# Test individual calculators
python -m calculators.runner
```

## Project Structure

```
sourcewell-project/
├── app/                    # Web interface module
├── calculators/           # Risk assessment suite
├── knowledge_base/        # Medical content management
├── llm/                   # AI explanation engine
├── data_models/          # Patient data validation
├── tests/                # Comprehensive test suite
├── data/                 # Medical content repository
├── docker-compose.yml    # Weaviate deployment
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Key Features

- **Privacy-First**: All processing occurs locally—no external data transmission
- **Evidence-Based**: Recommendation backed by peer-reviewed medical literature
- **Personalized**: Risk assessments tailored to individual and family health history
- **Transparent**: Complete citation tracking and source verification
- **Adaptive**: Graceful degradation with comprehensive error handling
- **Cross-Platform**: Seamless operation across Windows, macOS, and Linux
- **AI-Powered**: Local LLM with mandatory citation verification
- **Interactive**: Rich visualizations and intuitive user interface

## Medical Disclaimer

**Important**: This application provides educational health information only and is **NOT** a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions. Users assume full responsibility for health decisions. The information provided is for educational purposes and should not be used to diagnose or treat any health problem or disease.

All AI-generated explanations require clinical validation. The system includes fallback mechanisms but cannot guarantee 100% uptime or accuracy.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Development Status**: Academic Capstone Project - Advancing Evidence-Based Healthcare Technology
**Author**: Selin Birinci

*For detailed technical documentation, implementation guides, and API references, please refer to the individual module READMEs linked above.*
