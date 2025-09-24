"""
Knowledge Base Module

Medical content management with mandatory citation verification
and semantic search capabilities.
"""

import os
import logging
import weaviate
import sys
from pathlib import Path
from typing import Dict, Any
from .config import WEAVIATE_HTTP_PORT, WEAVIATE_GRPC_PORT
from .config import  SUPPORTED_CALCULATORS, REQUIRED_COLLECTIONS, MIN_GUIDELINES_REQUIRED

# Core component imports  
from .schema_setup import MedicalSchemaManager
from .content_ingester import MedicalContentIngester
from .search_engine import MedicalSearchEngine

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# version fallback configuration
# Update FALLBACK_VERSION after reaching a stable version
FALLBACK_VERSION = "0.1.0"
FALLBACK_STATUS = "Development-Fallback"
fallback_activated = False

try:
    from _version import __version__, __status__, get_version_info
    # Verify the imported function works correctly
    _ = get_version_info()
except Exception:
    __version__ = FALLBACK_VERSION
    __status__ = FALLBACK_STATUS
    fallback_activated = True
    
    def get_version_info():
        return {
            "platform_version": __version__,
            "status": __status__,
            "fallback_active": True
        }
    
# Public API definition
__all__ = [
    "MedicalSchemaManager",
    "MedicalContentIngester", 
    "MedicalSearchEngine",
    "get_system_info",
    "check_system_health",
    "SUPPORTED_CALCULATORS",
    "WEAVIATE_HTTP_PORT", 
    "WEAVIATE_GRPC_PORT",
    "SUPPORTED_CALCULATORS", 
    "REQUIRED_COLLECTIONS", 
    "MIN_GUIDELINES_REQUIRED",
    "__version__",
    "__status__"
]

def get_system_info() -> Dict[str, Any]:
    """
    Get system statistics and version information
    """
    try:
        version_info = get_version_info()
    except Exception as e:
        logging.error(f"Error getting version info: {e}", exc_info=True)
        version_info = {
            "platform_version": __version__,
            "status": __status__
        }
    
    info = {
        'version_info': version_info,
        'supported_calculators': SUPPORTED_CALCULATORS,
        'system_status': 'unknown'
    }
    
    # Add runtime statistics if system is operational
    try:
        with MedicalSearchEngine() as engine:
            stats = engine.get_knowledge_base_stats()
            info['content_statistics'] = stats
            info['total_documents'] = sum(stats.values())
            info['system_status'] = 'operational'
    except Exception as e:
        info['content_statistics'] = 'unavailable'
        info['total_documents'] = 0
        info['system_status'] = f'error: {str(e)}'
    
    return info

def check_system_health() -> Dict[str, Any]:
    """
    Perform system health verification.
    """
    
    health = {
        'platform_version': __version__,
        'status': __status__,
        'weaviate_connection': False,
        'schema_exists': False, 
        'content_available': False,
        'operational': False,
        'issues': []
    }
    
    client = None
    try:
        # Test Weaviate connectivity
        client = weaviate.connect_to_local(port=WEAVIATE_HTTP_PORT, grpc_port=WEAVIATE_GRPC_PORT)
        health['weaviate_connection'] = client.is_ready()
        
        if health['weaviate_connection']:
            # Verify required collections exist
            collections = client.collections.list_all()
            collection_names = {col.name for col in collections.values()}
            required_collections = REQUIRED_COLLECTIONS
            health['schema_exists'] = all(
                collection in collection_names for collection in required_collections
            )
            
            # Check content availability
            if health['schema_exists']:
                mg_collection = client.collections.get("MedicalGuideline")
                mg_count = mg_collection.aggregate.over_all(total_count=True).total_count
                ra_collection = client.collections.get("ResearchAbstract")
                ra_count = ra_collection.aggregate.over_all(total_count=True).total_count
                health['content_available'] = mg_count >= MIN_GUIDELINES_REQUIRED
                health['document_count_guidelines'] = mg_count
                health['document_count_abstracts'] = ra_count
                health['document_count_total'] = mg_count + ra_count
        
        # Overall operational status
        health['operational'] = all([
            health['weaviate_connection'],
            health['schema_exists'], 
            health['content_available']
        ])
        
        if not health['operational']:
            if not health['weaviate_connection']:
                health['issues'].append("Weaviate connection failed")
            if not health['schema_exists']:
                health['issues'].append("Database schema missing")
            if not health['content_available']:
                health['issues'].append("Insufficient medical content")
        
    except Exception as e:
        health['issues'].append(f"Health check failed: {str(e)}")
        logging.error(f"Health check failed: {e}", exc_info=True)

    finally:
        if client:
            try:
                client.close()
            except Exception:
                pass
    
    return health

# Configure healthcare-compliant logging with version tracking
def _setup_logging():
    """Configure package logging for healthcare compliance."""
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'%(asctime)s - SourceWell v{__version__} - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

_setup_logging()

if fallback_activated:
    logging.warning(f"version fallback activated - using v{__version__}")

logging.info(f"SourceWell Knowledge Base v{__version__} - {__status__}")