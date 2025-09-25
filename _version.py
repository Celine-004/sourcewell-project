"""
SourceWell Healthcare AI Platform - Version Management

This file centralizes version information for the entire SourceWell platform.
All modules import version data from here to maintain consistency.
Semantic Versioning.
"""
# application versioning
__version__ = "0.3.0"

#package metadata
__author__ = "Selin Birinci"
__description__ = "SourceWell - Evidence-based preventive health guidance platform"
__status__ = "Development - Core Calculators Operational"
__license__ = "MIT"

# component versioning
SCHEMA_VERSION = "1.1"           
CONTENT_VERSION = "2024-09-16"   
API_VERSION = "0.3"              

# Version history
VERSION_HISTORY = {
    "0.3.0": {
        "release_date": "2024-09-25",
        "status": "Development - Core Calculators Operational",
        "description": "Complete evidence-based risk calculator suite with comprehensive testing and clinical validation",
        "schema_version": "1.1",
        "content_version": "2024-09-16",
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
    "release_date": "2024-09-24",
    "status": "Development - Production Infrastructure Ready", 
    "description": "Production-ready infrastructure with centralized configuration, universal installer, and enhanced deployment capabilities",
    "schema_version": "1.1",
    "content_version": "2024-09-16",
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
        "release_date": "2024-09-20",
        "status": "Development - Knowledge Base Operational",
        "description": "First version release - Knowledge base backend operational",
        "schema_version": "1.0",
        "content_version": "2024-09-16",
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