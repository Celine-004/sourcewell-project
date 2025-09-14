# SourceWell Project

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://www.docker.com/)

> Evidence-based preventive health guidance platform combining validated clinical risk calculators with AI-powered explanations and mandatory citation verification.

## Project Overview

SourceWell Project addresses the gap between generic health advice and personalized medical guidance by combining validated clinical risk calculators with AI-powered explanations sourced from peer-reviewed medical literature. It empowers users with transparent, evidence-backed insights tailored to their personal and family health history.

### Problem Statement
Individuals often receive generalized health advice that doesn't account for their unique personal and family medical history. This can lead to missed prevention opportunities, reduced engagement with healthcare recommendations, and a lack of trust in AI-generated insights due to opacity.

### Solution Approach
The project implements a hybrid intelligent system that:
- **Collects Tiered Health Data**: Adapts to user's medical knowledge level (basic to clinical-grade).
- **Executes Validated Risk Calculations**: Utilizes established medical formulas (FINDRISC, Modified Framingham, Colorectal screening).
- **Retrieves Relevant Medical Evidence**: Employs semantic search on a curated knowledge base.
- **Generates Personalized Explanations**: Provides plain-language insights tailored to the user.
- **Enforces Mandatory Citation Verification**: Ensures every medical claim is traceable to its source.
- **Offers Interactive Prevention Coaching**: Guides users with actionable, evidence-backed steps.

### Key Innovation
**Mandatory Citation Verification**: A core differentiator, this system automatically verifies that every medical claim presented to the user is directly supported by passages from curated, peer-reviewed medical sources. Any claim without verifiable evidence is either removed or flagged, ensuring unprecedented accuracy, transparency, and trustworthiness in AI-generated health guidance.

## Technical Architecture

### System Design
The application operates on a modular, agentic architecture orchestrated to seamlessly integrate validated medical science with advanced AI capabilities.


### Technology Stack
- **Frontend**: Streamlit with custom CSS for an elegant, calming user experience.
- **Backend**: FastAPI for robust, asynchronous API orchestration and business logic.
- **AI Models**: 
    - **Phi-3 Mini**: A local, open-source large language model for generating plain-language explanations (optimized for GPU inference).
    - **Sentence-Transformers (all-MiniLM-L6-v2)**: For creating embeddings for semantic search.
- **Knowledge Base**: Weaviate vector database for storing and semantically searching medical guidelines and research abstracts with rich metadata.
- **Risk Calculators**: Custom Python implementations of clinically validated formulas (FINDRISC, Modified Framingham, Colorectal Cancer Screening).
- **Deployment**: Docker Compose for containerizing Weaviate, ensuring easy setup and cross-platform compatibility.
- **Platform**: Designed for Windows (with WSL2), macOS, and Linux; optimized for NVIDIA GPUs (like GTX 1060).

### Core Components

**1. Tiered Data Collection**
An adaptive input system that caters to varying levels of user medical knowledge:
- **Tier 1 (Universal Access)**: Basic demographics (age, sex, height, weight for BMI), lifestyle factors (smoking, activity), chronic conditions (checkboxes), and family history.
- **Tier 2 (Health-Aware)**: Exact blood pressure measurements (systolic/diastolic), ethnicity, more detailed family history.
- **Tier 3 (Health-Savvy)**: Specific lab values (cholesterol, glucose), detailed medical history.

**2. Evidence-Based Risk Assessment**
Implementation of established medical risk calculators:
- **FINDRISC**: For 10-year Type 2 diabetes risk.
- **Modified Framingham CVD Risk**: For 10-year cardiovascular disease risk, using exact BP readings.
- **Colorectal Cancer Screening**: Guidelines-based recommendations.
These calculators provide baseline risk scores, which then inform the AI's explanation and evidence retrieval.

**3. Semantic Knowledge Retrieval**
A curated knowledge base of open-source medical guidelines and PubMed abstracts is stored in Weaviate. This system performs semantic (meaning-based) searches to find highly relevant passages, ensuring that all retrieved information comes with complete citation metadata (PubMed IDs, DOIs, publication dates, evidence grades).

**4. AI Explanation with Citation Enforcement**
The local Phi-3 Mini LLM synthesizes the retrieved medical passages into plain-language explanations and personalized coaching advice. Crucially, a custom **Citation Verifier** module analyzes the LLM's output, automatically identifying and removing any medical claims that cannot be directly traced and cited to the provided evidence, thus maintaining the highest standard of medical accuracy and transparency.

## Quick Start

### Prerequisites
Before you begin, ensure your system meets these requirements:
- **Python**: Version 3.11+ with `pip`
- **Docker Desktop**: Installed and running (with WSL2 enabled for Windows)
- **NVIDIA GPU**: Recommended for faster AI inference (GTX 1060 6GB+ VRAM)
- **RAM**: 16GB or more
- **Storage**: ~15GB free space (preferably on D: drive for Windows users)

### Installation
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/[your-github-username]/sourcewell-project.git
    cd sourcewell-project
    ```
2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv healthcare_env
    # For Windows:
    healthcare_env\Scripts\activate
    # For macOS/Linux:
    # source healthcare_env/bin/activate
    ```
3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Start Weaviate Knowledge Base (using Docker Compose):**
    ```bash
    docker-compose up -d
    ```
5.  **Start FastAPI Backend API:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    ```
6.  **Start Streamlit Frontend:**
    ```bash
    streamlit run app/ui.py
    ```

### Usage
1.  Open your web browser and navigate to `http://localhost:8501`.
2.  Interact with the "Heritage" section to input personal and family health data.
3.  Click "Assess My Health Risks" to generate a personalized report.
4.  Explore the "Report" and "Coaching" sections for evidence-backed insights and recommendations.

## Key Features

-   **Adaptive Intelligence**: Dynamically selects appropriate risk calculators and tailors explanations based on available user data.
-   **Citation Integrity**: Every medical claim is automatically verified and linked to its source, ensuring unparalleled trustworthiness.
-   **Privacy-First**: All data processing, including AI inference, occurs locally on your machine, with no external data transmission.
-   **Cross-Platform Compatibility**: Designed to run seamlessly across Windows, macOS, and Linux environments.
-   **Modular Design**: A highly organized architecture allows for independent updates, easy integration of new calculators, and future expansion.
-   **Elegant User Experience**: A calming, professional interface with a calming color palette, inspired by a family tree aesthetic.

## Medical Disclaimer

This application provides educational health information only and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions. Users assume full responsibility for health decisions. The information provided is for educational purposes and should not be used to diagnose or treat any health problem or disease.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed as part of AI Solutions Architect Capstone Project - Advancing evidence-based healthcare technology.*