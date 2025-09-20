"""
SourceWell Healthcare AI Platform - Version Management

This file centralizes version information for the entire SourceWell platform.
All modules import version data from here to maintain consistency.
Semantic Versioning.
"""
# application versioning
__version__ = "0.1.0"

#package metadata
__author__ = "Selin Birinci"
__description__ = "Evidence-based preventive health guidance platform"
__status__ = "Development - Knowledge base operational"
__license__ = "MIT"

# component versioning
SCHEMA_VERSION = "1.0"           
CONTENT_VERSION = "2024-09-16"   
API_VERSION = "0.1"              

# Version history - starting fresh and honest
VERSION_HISTORY = {
    "0.1.0": {
        "release_date": "2024-09-20",
        "status": "Development - Knowledge Base Operational",
        "description": "First version release - Knowledge base backend operational",
        "schema_version": "1.0",
        "content_version": "2024-09-16",
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