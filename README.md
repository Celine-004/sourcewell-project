# SourceWell Project

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://www.docker.com/)

> Evidence-based preventive health guidance platform combining validated clinical risk calculators with AI-powered explanations, mandatory citation verification, and persistent user sessions.

## Problem Statement & Solution

### The Challenge

Individuals often receive generalized health advice that doesn't account for their unique personal and family medical history. This leads to missed prevention opportunities, reduced engagement with healthcare recommendations, and a lack of trust in AI-generated insights due to opacity.

### Our Approach

SourceWell implements a hybrid intelligent system that collects patient health data with clinical validation, executes validated risk calculations (FINDRISC, Modified Framingham, USPSTF Colorectal Screening), retrieves relevant medical evidence through semantic search on a curated knowledge base, generates personalized explanations using local LLM inference with mandatory citation verification, and provides an AI coaching chat for follow-up health questions — all with persistent user sessions backed by SQLite.

## Key Innovation: Mandatory Citation Verification

SourceWell automatically verifies that every medical claim presented to users is directly supported by passages from curated, peer-reviewed medical sources. Any claim without verifiable evidence is either removed or flagged, ensuring accuracy, transparency, and trustworthiness in AI-generated health guidance.

## System Architecture

```
SourceWell Platform 
├── Frontend (Streamlit)         # Interactive web interface with login/session management 
├── User Database (SQLite)       # Persistent sessions, chat history, patient data 
├── Risk Calculators             # Validated clinical assessments (FINDRISC, Framingham, Colorectal) 
├── Knowledge Base (Weaviate)    # Medical literature & guidelines with semantic search 
├── LLM Engine (Qwen3-4B, 4-bit) # AI explanation generation via local GPU inference 
├── Citation Verifier            # Mandatory evidence verification 
├── AI Coaching Chat             # Context-aware health Q&A 
└── Patient Data Model           # Clinical validation system
```

## Platform Compatibility

SourceWell has been validated on the following platforms:

**Validated:**
- **Linux** (Ubuntu 22.04+) — Primary development and deployment platform. Full GPU acceleration with NVIDIA CUDA.
- **Windows** (Windows 10/11 with WSL2) — Tested via WSL2 Ubuntu environment. Native Windows operation requires manual bitsandbytes configuration.

**Not Validated:**
- **macOS** — The application should function on macOS (CPU mode or Apple Silicon MPS), but this has not been tested. GPU acceleration on macOS requires verification.

If you encounter platform-specific issues during setup, the `setup_sourcewell.py` script includes hardware detection and will attempt to configure dependencies automatically. The included `gpu_diagnostic.py` script can help identify GPU and CUDA configuration issues.

## Core Modules

### [Risk Calculator Suite](calculators/README.md)

Evidence-based preventive health risk calculators with knowledge base integration: FINDRISC (Finnish Diabetes Risk Score), Modified Framingham (cardiovascular disease risk with AHA/ACC guidelines), and USPSTF 2021 Colorectal Cancer Screening recommendations. All calculators query the Weaviate knowledge base for dynamic citation retrieval and fall back to validated static citations when the knowledge base is unavailable.

### [Medical Knowledge Base](knowledge_base/README.md)

Comprehensive medical content management with semantic search, built on Weaviate 1.24.1 vector database with a text2vec-transformers vectorizer (sentence-transformers/all-MiniLM-L6-v2). Supports clinical guidelines and research abstracts with Vancouver-style citation generation and calculator-specific content filtering.

### [LLM Engine](llm/README.md)

AI explanation system powered by Qwen3-4B (4-bit quantized) running on local GPU. Uses SDPA attention optimization for NVIDIA Pascal+ GPUs, RAG-based evidence retrieval, condition-specific prompt templates (diabetes, cardiovascular, colorectal), dynamic source configuration, and an AI coaching chat for personalized follow-up questions.

### [Web Interface](app/README.md)

Interactive Streamlit application with user authentication (login/register), session persistence via SQLite, multi-page navigation (Patient History, Assessment, Report, Coaching), interactive risk visualization with Plotly, AI-powered explanations with citation verification, and a coaching chat interface.

### [Patient Data Model](data_models/README.md)

Clinical validation system for adult preventive healthcare with evidence-based validation ranges, automatic BMI calculation with WHO categorization, biological plausibility validation, and clean data export for calculator integration.

### [Medical Content Repository](data/medical_content/README.md)

Curated medical content from ADA, AHA/ACC, and USPSTF guidelines with complete citation metadata, quality assurance workflows, and automated ingestion with archival.

### [Test Suite](tests/README.md)

Comprehensive testing for clinical accuracy, knowledge base integrity, AI integration, and healthcare compliance validation.

## Technology Stack

The platform is built on Streamlit for the web interface, Qwen3-4B (4-bit quantized via bitsandbytes) for local LLM inference, Weaviate vector database with sentence-transformers for semantic search, SQLite for user management and session persistence, PyTorch with CUDA for GPU-accelerated inference, Plotly for interactive data visualization, and Docker for Weaviate deployment.

## Quick Start

### Prerequisites

- **Python 3.12+** with pip
- **Docker** installed and running (for Weaviate)
- **8GB+ RAM** (16GB recommended)
- **NVIDIA GPU** with 4GB+ VRAM recommended (GTX 1060 or newer; CPU fallback available)
- **15GB storage** for models and cache

### Installation

**1. Clone and set up the environment:**

```bash
git clone https://github.com/Celine-004/sourcewell-project
cd sourcewell-project

python3 -m venv healthcare_env
source healthcare_env/bin/activate    # Linux/macOS
# healthcare_env\Scripts\activate     # Windows

python setup_sourcewell.py --auto
```

**2. Start core 

```bash
docker compose up -d

python -m knowledge_base.schema_setup setup
python -m knowledge_base.content_ingester
```

**3. Launch the application:**
```bash
streamlit run app/main.py
```

**4. Access the platform** at *http://localhost:8501*. Register an account, complete patient data collection, run risk assessments, and review AI-generated insights with citations.

### GPU Diagnostics

If you encounter GPU or CUDA issues during setup, run the included diagnostic script:

```bash
python gpu_diagnostic.py
```

This reports your Python version, PyTorch/CUDA status, GPU memory, bitsandbytes compatibility, and transformer library versions.

### Quick Test

```bash
python -m tests
python -m calculators.runner
```

### Project Structure

```
sourcewell-project/
├── app/                       # Web interface module
│   ├── main.py               # Entry point with login/session management
│   ├── data/                 # SQLite database module
│   └── ui/                   # Pages, components, styles
├── calculators/              # Risk assessment suite
├── knowledge_base/           # Medical content management
├── llm/                      # AI explanation engine
│   ├── qwen3_engine.py      # Primary engine (Qwen3-4B)
│   ├── engines/             # Model wrappers (qwen3_wrapper.py)
│   ├── rag/                 # RAG retrieval
│   └── utils/               # Prompt templates
├── data_models/             # Patient data validation
├── tests/                   # Test suite
├── data/                    # Medical content repository
├── gpu_diagnostic.py        # GPU/CUDA diagnostic utility
├── setup_sourcewell.py      # Automated setup with hardware detection
├── docker-compose.yml       # Weaviate + vectorizer deployment
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Key Features

SourceWell processes all data locally with no external data transmission. All recommendations are backed by peer-reviewed medical literature with complete citation tracking. Risk assessments are tailored to individual and family health history. The system includes an AI coaching chat for follow-up questions, persistent user sessions across browser restarts, graceful degradation with comprehensive error handling, and local LLM inference with mandatory citation verification.

### Medical Disclaimer

**Important:** This application provides educational health information only and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions. All AI-generated explanations require clinical validation.

### License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) for details.

---

**Development Status:** Academic Capstone Project — Advancing Evidence-Based Healthcare Technology 
**Author:** Selin Birinci

*For detailed technical documentation, refer to the individual module READMEs linked above.*
