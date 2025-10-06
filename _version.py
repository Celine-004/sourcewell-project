"""
SourceWell Healthcare AI Platform - Version Management

This file centralizes version information for the entire SourceWell platform.
All modules import version data from here to maintain consistency.
Semantic Versioning.
"""
# application versioning
__version__ = "0.4.0"

#package metadata
__author__ = "Selin Birinci"
__description__ = "SourceWell - Evidence-based preventive health guidance platform"
__status__ = "Beta - Full Stack Operational with AI and Web Interface"
__license__ = "MIT"

# component versioning
SCHEMA_VERSION = "1.1"           
CONTENT_VERSION = "2025-09-16"   
API_VERSION = "0.4"              

# Version history
VERSION_HISTORY = {
    "0.4.0": {
        "release_date": "2025-10-6",
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
        "calculator_integration": [
            "Extended existing FINDRISC, Framingham, and Colorectal calculators with AI explanation generation",
            "Integrated MultiCalculatorRunner with web interface and visualization pipeline",
            "PatientData model integration with Streamlit form components"
        ],
        "technical_achievements": [
            "Full-stack integration: Streamlit UI ↔ Risk Calculators ↔ LLM Engine ↔ Knowledge Base",
            "Robust LLM engine with multiple initialization strategies and graceful degradation",
            "Cross-platform PyTorch 2.3.1 installation with GPU acceleration support and CPU fallback",
            "Memory optimization support via bitsandbytes 0.41.1 (with Windows compatibility fallbacks)",
            "Comprehensive error handling and health monitoring across all components",
            "RAG integration with knowledge base retrieval and citation verification pipeline"
        ],
        "infrastructure_improvements": [
            "Cross-platform installation script with multi-vendor GPU detection and robust timeout handling",
            "Project-local cache management: all HuggingFace models, pip cache, and temporary files stored in project/.cache directory",
            "Environment variable configuration directs all caches to project folder (HF_HOME, PIP_CACHE_DIR, TMP/TEMP, TORCH_HOME)",
            "Standardized on PyTorch 2.3.1",
            "Requirements updated for AI/UI stack: transformers, sentence-transformers, streamlit, plotly",
            "Added accelerate 1.10.1 for Hugging Face model optimization",
            "Installation verification with component health checks and fallback validation",
            "Robust timeout handling for large model downloads (up to 30 minutes)",
            "Cache path persistence in configuration file for cross-process consistency"
        ],
        "ai_capabilities": [
            "Microsoft Phi-3 Mini 4K model integration for contextual medical explanations",
            "RAG integration with knowledge base retrieval and citation verification",
            "Intelligent fallback to text-based summaries when AI components fail",
            "Hardware-optimized inference with GPU acceleration and 4-bit quantization",
            "Structured response format with confidence scores(will be dinamic in the next update) and verification metadata"
        ],
        "medical_compliance": [
            "AI-generated explanations include medical disclaimers and professional consultation guidance",
            "Citation verification pipeline maintains evidence-based recommendations when knowledge base available",
            "Fallback mechanisms ensure system availability when AI components unavailable",
            "Structured error handling prevents incomplete medical information delivery",
            "All therapy recommendations include 'Consult your medical provider' disclaimers"
        ],
        "system_requirements": [
            "Disk space: ~8GB for AI models (stored in project/.cache directory)",
            "RAM: 8GB minimum, 16GB recommended for GPU acceleration",
            "Network: Stable connection required for initial model download (~7-8GB)",
            "PyTorch 2.3.1 with CUDA 12.1/11.8 support or CPU fallback"
        ],
        "development_status": [
            "Core functionality implemented and locally tested on primary development platform(Windows)",
            "Cross-platform installation support implemented with hardware detection",
            "AI model performance varies by hardware (5-180 seconds per explanation)",
            "Medical content accuracy requires professional validation before clinical deployment"
        ],
        "notes": "Major expansion: Adds AI explanation engine and comprehensive web interface to existing calculator foundation from 0.3.0. Provides complete healthcare AI platform with evidence-based risk assessment, intuitive user interface, and AI-powered insights while maintaining medical safety standards. PyTorch 2.3.1 standardization ensures broad compatibility. Project-local storage keeps all downloads contained within project directory for predictable file management. Technical capabilities documented; comprehensive cross-platform testing and medical validation recommended before production deployment."
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
            "Enhanced test framework with calculator-specific validation and CI/CD integration",
        ],
        "breaking_changes": "None - new functionality only",
        "features": [
            "FINDRISC diabetes risk calculator with personalized evidence-based recommendations",
            "Modified Framingham 10-year CVD risk with AHA/ACC 2017/2019 guideline compliance",
            "USPSTF 2021 colorectal screening recommendations with risk stratification",
            "MultiCalculatorRunner for integrated patient assessment and priority action generation",
            "PatientData model with WHO BMI categorization and comprehensive clinical validation",
            "Knowledge base integration with mandatory citation verification and robust fallbacks",
            "Clinical safety disclaimers for medication and therapy recommendations",
            "Comprehensive calculator test suite with clinical accuracy validation"
        ],
        "technical_achievements": [
            "100% calculator test success rate with 11 comprehensive test cases",
            "Clinical accuracy validation for all three risk assessment domains",
            "Knowledge base integration testing with fallback behavior validation",
            "Medical compliance verification including therapy disclaimers",
            "Realistic performance expectations for KB-integrated assessments"
        ],
        "medical_compliance": [
            "All therapy recommendations include 'Consult your medical provider' disclaimers",
            "Vancouver-style citation verification for all medical recommendations",
            "Evidence-based fallbacks ensure clinical guidance always available",
            "Clinical validation ranges based on WHO, AHA/ACC, ADA, USPSTF guidelines"
        ],
        "notes": "Major functional milestone - SourceWell now provides genuine clinical utility for preventive healthcare risk assessment"
    },

    "0.2.0": {
    "release_date": "2025-09-24",
    "status": "Development - Production Infrastructure Ready", 
    "description": "Production-ready infrastructure with centralized configuration, universal installer, and enhanced deployment capabilities",
    "schema_version": "1.1",
    "content_version": "2025-09-16",
    "api_version": "0.2",
    "api_changes": "Added centralized configuration module (knowledge_base.config) with environment-aware port management; enhanced test framework with CLI execution",
    "breaking_changes": "Weaviate port configuration moved from hardcoded values to centralized config module",
    "features": [
        "Universal PyTorch installer with cross-platform GPU detection (NVIDIA, AMD, Intel, Apple Silicon)",
        "Centralized configuration management with environment variable support",
        "Production-ready knowledge base interface with health monitoring capabilities", 
        "Intelligent test suite with dynamic content allocation and CI/CD integration",
        "Enhanced schema with complete medical metadata and GPU-optimized vector indexing",
        "CLI test execution via 'python -m tests' with professional exit codes"
    ],
    "infrastructure_improvements": [
        "Adaptive storage management for space-constrained development environments",
        "Robust PyTorch installation with 30-minute timeouts and automatic CPU fallback", 
        "HuggingFace cache modernization (TRANSFORMERS_CACHE -> HF_HOME)",
        "Environment variable propagation for subprocess operations(TMP/TEMP/PIP_CACHE_DIR)",
        "Healthcare-grade error handling with comprehensive audit logging",
        "Cross-platform configuration management for deployment flexibility"
    ],
    "pending_components": [
        "Risk calculator implementations (FINDRISC, ModifiedFramingham, ColorectalScreening)",
        "AI explanation generation with Phi-3 Mini", 
        "Streamlit web interface",
        "FastAPI REST endpoints"
    ],
    "medical_content": "Curated ADA, ACC/AHA, and USPSTF guidelines with research abstracts",
    "notes": "Core dependencies streamlined (torch removed from requirements.txt); infrastructure hardened for production deployment scenarios"
},
    "0.1.0": {
        "release_date": "2025-09-20",
        "status": "Development - Knowledge Base Operational",
        "description": "First version release - Knowledge base backend operational",
        "schema_version": "1.0",
        "content_version": "2025-09-16",
        "api_version": "0.1",
        "api_changes": "Initial public API established: MedicalSchemaManager, MedicalContentIngester, MedicalSearchEngine classes with documented method signatures",
        "breaking_changes": None,
        "features": [
            "Weaviate v4 semantic search with NamedVectors integration",
            "Dual-layer SHA256 deduplication system for data integrity",
            "Medical content ingestion with Vancouver-style citations",
            "Calculator-specific filtering (FINDRISC, ModifiedFramingham, ColorectalScreening)",
            "Comprehensive testing framework with infrastructure validation",
        ],
                "pending_components": [
            "Risk calculator implementations (FINDRISC, ModifiedFramingham, ColorectalScreening)",
            "AI explanation generation with Phi-3 Mini",
            "Streamlit web interface",
            "FastAPI REST endpoints"
        ],
        "medical_content": "Curated ADA, ACC/AHA, and USPSTF guidelines with research abstracts",
        "notes": "Backend infrastructure complete and tested, ready for calculator implementation"
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