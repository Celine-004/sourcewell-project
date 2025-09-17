"""
Knowledge Base Module

Medical content management with mandatory citation verification
and semantic search capabilities.
"""
from .schema_setup import MedicalSchemaManager
from .content_ingester import MedicalContentIngester  
from .search_engine import MedicalSearchEngine

__version__ = "1.0.0"
__all__ = ["MedicalSchemaManager", "MedicalContentIngester", "MedicalSearchEngine"]