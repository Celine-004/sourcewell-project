"""
SourceWell Healthcare AI Platform - Version Management

This file centralizes version information for the entire SourceWell platform.
All modules import version data from here to maintain consistency.
Semantic Versioning.
"""
# application versioning
__version__ = "1.0.3"

# package metadata
__author__ = "Selin Birinci"
__description__ = "SourceWell - Evidence-based preventive health guidance platform"
__status__ = "Release - Full Platform Operational"
__license__ = "MIT"

# component versioning
SCHEMA_VERSION = "1.1"
CONTENT_VERSION = "2025-09-16"
API_VERSION = "1.0"

# Version history
VERSION_HISTORY = {
    "1.0.3": {
        "release_date": "2026-07-09",
        "status": "Release - Full Platform Operational",
        "description": "Align UI with data model: clinical fields are truly optional with None defaults",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "1.0",
        "api_changes": [],
        "breaking_changes": "None",
        "fixes": [
            "Clinical measurements (BP, cholesterol, waist) now render as empty fields instead of placeholder values",
            "UI aligned with PatientData model where clinical fields are Optional[int] = None",
            "Calculators gracefully report which fields are missing rather than crashing",
            "Help text indicates which calculator requires each field"
        ],
        "notes": "Colorectal screening runs independently of clinical measurements. FINDRISC and Framingham display clear messages when required fields are absent."
    },

    "1.0.2": {
        "release_date": "2026-07-08",
        "status": "Release - Full Platform Operational",
        "description": "Wire calculator selection checkboxes and align Framingham display to AHA/ACC 2018 guidelines",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "1.0",
        "api_changes": [
            "RiskDashboard.run_risk_assessment() now accepts selected_calculators parameter"
        ],
        "breaking_changes": "None",
        "fixes": [
            "Assessment page calculator checkboxes now control which calculators execute",
            "Framingham risk display uses four-tier AHA/ACC 2018 classification (low/borderline/intermediate/high)",
            "Gauge chart thresholds aligned to clinical cutoffs (5%, 7.5%, 20%)",
            "Risk factor summary uses intermediate threshold at 7.5% instead of 10%",
            "Comparison chart title clarified to 'Estimated 10-Year Risk: Diabetes vs. Cardiovascular'"
        ],
        "notes": "Previously, calculator selection checkboxes were cosmetic and all three calculators always ran."
    },

    "1.0.1": {
        "release_date": "2026-07-08",
        "status": "Release - Full Platform Operational",
        "description": "Correct data flow documentation in LLM README",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "1.0",
        "api_changes": [],
        "breaking_changes": "None",
        "fixes": [
            "LLM README data flow corrected: RAG evidence retrieval precedes prompt construction, not the reverse"
        ],
        "notes": "Documentation-only change."
    },

    "1.0.0": {
        "release_date": "2026-07-07",
        "status": "Release - Full Platform Operational",
        "description": "First stable release. Complete platform with Qwen3-4B AI engine, user management, coaching chat, session persistence, and full documentation. Validated on Linux.",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "1.0",
        "api_changes": [
            "All READMEs updated to reflect current architecture",
            "Root README documents platform compatibility (Linux validated, Windows via WSL2, macOS not validated)",
            "LLM README documents Qwen3 engine, SDPA attention, prompt templates",
            "App README documents login/register, session persistence, coaching chat"
        ],
        "breaking_changes": "None",
        "new_features": [],
        "notes": "Documentation milestone marking the first complete, stable, and fully documented release of the SourceWell platform."
    },

    "0.7.0": {
        "release_date": "2026-07-02",
        "status": "Beta - User Management Added",
        "description": "Add user authentication, session persistence, and cross-session data restoration",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.7",
        "api_changes": [
            "Added app/data/database.py with UserDatabase class",
            "Added login/register flow in app/main.py",
            "Added session picker for restoring previous sessions"
        ],
        "breaking_changes": "app/main.py restructured with authentication gate before application launch",
        "new_features": [
            "SQLite-based user registration and login with SHA-256 password hashing",
            "Session persistence: patient data, risk results, and chat history stored per session",
            "Session picker allows users to resume previous sessions or start new ones",
            "Form fields pre-fill from saved session data via _get_saved helper",
            "Key remapping between calculator output keys and form field names on session restore",
            "Action plan download bug fixed (non-dict risk result handling)"
        ],
        "notes": "Database stored at .db/sourcewell.db, excluded from git. All SQL uses parameterized queries."
    },

    "0.6.0": {
        "release_date": "2026-06-30",
        "status": "Beta - Coaching Chat Added",
        "description": "Add AI coaching chat with context-aware responses and fix Chinese character leaks",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.6",
        "api_changes": [
            "Added generate_coaching_response() to Qwen3Engine",
            "Added chat UI to coaching page with session state history"
        ],
        "breaking_changes": "None",
        "new_features": [
            "AI coaching chat at bottom of coaching page with clinical advisor tone",
            "Context-aware responses using patient risk results and conversation history",
            "Non-ASCII character filtering via regex in qwen3_wrapper.py and qwen3_engine.py",
            "setup_sourcewell.py updated: DEFAULT_AI_MODEL_ID changed from Phi-3 to Qwen/Qwen3-4B",
            "Warning suppression for weaviate-client deprecation, bitsandbytes save_pretrained, and torch_dtype"
        ],
        "notes": "Coaching chat maintains last 6 messages for conversational context. Chinese character leaks from Qwen3 tokenizer resolved with post-generation regex filter."
    },

    "0.5.0": {
        "release_date": "2026-06-30",
        "status": "Beta - Qwen3 Migration",
        "description": "Migrate AI engine from Phi-3 Mini to Qwen3-4B with 4-bit quantization, condition-specific prompts, and dynamic source configuration",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.5",
        "api_changes": [
            "Added llm/qwen3_engine.py as primary engine replacing phi3_engine.py",
            "Added llm/engines/qwen3_wrapper.py for model loading and generation",
            "Refactored llm/utils/prompt_templates.py with build_system_prompt and build_report_prompt",
            "Updated app/ui/pages/report.py to import Qwen3Engine"
        ],
        "breaking_changes": "Phi-3 engine archived. Qwen3Engine is now the active LLM engine. Report page imports changed.",
        "new_features": [
            "Qwen3-4B inference with 4-bit NF4 double quantization via bitsandbytes (~2.6GB VRAM)",
            "SDPA attention optimization for NVIDIA Pascal+ GPUs with eager fallback",
            "Condition-specific prompt templates: diabetes, cardiovascular, colorectal, general",
            "Prompts restrict model to discussing only the selected condition",
            "Dynamic source configuration: adjustable source count and character limits per explanation type",
            "Detailed analysis mode for extended 4-6 paragraph explanations",
            "Confidence metric based on evidence coverage ratio instead of hardcoded 0.85",
            "Verification score and confidence displayed as separate metrics in UI",
            "Citation verifier double-verification bug fixed",
            "Quick summary uses generate_with_system_prompt to prevent Chinese character output"
        ],
        "notes": "Qwen3-4B selected over Qwen3-8B due to GTX 1060 VRAM constraints (2.6GB vs 5GB+). Phi-3 files retained for reference. Main branch merged into feature branch to incorporate Linux GPU fixes before migration."
    },

    "0.4.2": {
        "release_date": "2026-06-24",
        "status": "Beta - Linux GPU Fixes",
        "description": "Resolve Linux GPU inference failures and refactor prompt templates",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.4",
        "api_changes": [
            "Refactored prompt_templates.py: separated build_system_prompt and build_report_prompt",
            "Fixed citation_verifier.py import path"
        ],
        "breaking_changes": "prompt_templates.py API changed: build_explanation_prompt replaced with build_system_prompt and build_report_prompt",
        "fixes": [
            "Resolved GPU inference fallback failure on Linux (Ubuntu 22.04, GTX 1060, CUDA 12.1)",
            "Fixed citation verifier import path mismatch",
            "Restructured prompt templates with separated system and report prompt construction"
        ],
        "notes": "Root cause was cascading compatibility issue between transformers 4.43.0, accelerate 1.10.1, and bitsandbytes on Linux with Python 3.12 and PyTorch 2.3.1."
    },

    "0.4.1": {
        "release_date": "2025-10-30",
        "status": "Beta - Maintenance",
        "description": "Dependency updates, setup improvements, system tests, and documentation",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.4",
        "api_changes": [],
        "breaking_changes": "None",
        "improvements": [
            "Updated dependency versions in requirements.txt",
            "Added AI model pre-download capability to setup script with local cache management",
            "Added full system test suite (test_full_system.py)",
            "Added centralized config file (sourcewell_config.json)",
            "Added Streamlit UI application module",
            "Added prompt template utilities for LLM module",
            "Added RAG retrieval engine for knowledge base integration",
            "Added Phi-3 model wrapper with GPU detection and quantization",
            "Added LLM module with engine orchestration",
            "Updated all module READMEs"
        ],
        "notes": "Incremental improvements building on 0.4.0 foundation. All components added as part of the initial full-stack integration."
    },

    "0.4.0": {
        "release_date": "2025-10-06",
        "status": "Beta - Full Stack Operational with AI and Web Interface",
        "description": "Extends evidence-based calculator suite with AI-powered medical explanations via Phi-3 Mini and comprehensive Streamlit web interface, plus enhanced installation and deployment capabilities",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.4",
        "api_changes": [
            "Added LLM module with Phi-3 Mini engine, citation verification, and structured explanation generation",
            "Introduced Streamlit web application with multi-page navigation",
            "Enhanced setup script with hardware-aware PyTorch 2.3.1 installation and project-local cache management",
            "Extended calculator integration with AI explanation pipeline and visualization components"
        ],
        "breaking_changes": "None - additive functionality only",
        "new_features": [
            "AI-powered medical explanation generation using Microsoft Phi-3 Mini model",
            "Multi-page Streamlit web interface: Patient History, Assessment, Report, Coaching",
            "Interactive risk visualization with Plotly charts, gauges, and color-coded dashboards",
            "Citation verification system with AI claim validation against knowledge base",
            "Hardware-aware installation with GPU detection (NVIDIA, AMD, Intel, Apple Silicon)",
            "Project-local storage management - all downloads and caches stored within project directory",
            "Optional AI model predownloading for offline operation capability",
            "Comprehensive error handling and graceful degradation for AI components"
        ],
        "notes": "Major expansion: Adds AI explanation engine and comprehensive web interface to existing calculator foundation. Development platform: Windows."
    },

    "0.3.0": {
        "release_date": "2025-09-25",
        "status": "Development - Core Calculators Operational",
        "description": "Complete evidence-based risk calculator suite with comprehensive testing and clinical validation",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.3",
        "api_changes": [
            "Added complete risk calculator API with MultiCalculatorRunner orchestration",
            "Added PatientData model with WHO BMI calculation and robust input filtering",
            "Enhanced test framework with calculator-specific validation"
        ],
        "breaking_changes": "None - new functionality only",
        "new_features": [
            "FINDRISC diabetes risk calculator with personalized evidence-based recommendations",
            "Modified Framingham 10-year CVD risk with AHA/ACC 2017/2019 guideline compliance",
            "USPSTF 2021 colorectal screening recommendations with risk stratification",
            "MultiCalculatorRunner for integrated patient assessment and priority action generation",
            "PatientData model with WHO BMI categorization and comprehensive clinical validation",
            "Knowledge base integration with mandatory citation verification and robust fallbacks",
            "Clinical safety disclaimers for medication and therapy recommendations",
            "Comprehensive calculator test suite with clinical accuracy validation"
        ],
        "notes": "Major functional milestone - SourceWell now provides genuine clinical utility for preventive healthcare risk assessment."
    },

    "0.2.0": {
        "release_date": "2025-09-24",
        "status": "Development - Production Infrastructure Ready",
        "description": "Production-ready infrastructure with centralized configuration, universal installer, and enhanced deployment capabilities",
        "schema_version": "1.1",
        "content_version": "2025-09-16",
        "api_version": "0.2",
        "api_changes": [
            "Added centralized configuration module with environment-aware port management",
            "Enhanced test framework with CLI execution"
        ],
        "breaking_changes": "Weaviate port configuration moved from hardcoded values to centralized config module",
        "new_features": [
            "Universal PyTorch installer with cross-platform GPU detection (NVIDIA, AMD, Intel, Apple Silicon)",
            "Centralized configuration management with environment variable support",
            "Production-ready knowledge base interface with health monitoring capabilities",
            "Intelligent test suite with dynamic content allocation",
            "CLI test execution via 'python -m tests' with professional exit codes"
        ],
        "notes": "Infrastructure hardened for production deployment scenarios."
    },

    "0.1.0": {
        "release_date": "2025-09-20",
        "status": "Development - Knowledge Base Operational",
        "description": "First version release - Knowledge base backend operational",
        "schema_version": "1.0",
        "content_version": "2025-09-16",
        "api_version": "0.1",
        "api_changes": [
            "Initial public API: MedicalSchemaManager, MedicalContentIngester, MedicalSearchEngine"
        ],
        "breaking_changes": None,
        "new_features": [
            "Weaviate v4 semantic search with NamedVectors integration",
            "Dual-layer SHA256 deduplication system for data integrity",
            "Medical content ingestion with Vancouver-style citations",
            "Calculator-specific filtering (FINDRISC, ModifiedFramingham, ColorectalScreening)",
            "Comprehensive testing framework with infrastructure validation"
        ],
        "notes": "Backend infrastructure complete and tested, ready for calculator implementation."
    }
}


def get_version_info():
    """Get comprehensive version information."""
    return {
        "platform_version": __version__,
        "status": __status__,
        "content_version": CONTENT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "api_version": API_VERSION,
        "release_info": VERSION_HISTORY.get(__version__, {})
    }
