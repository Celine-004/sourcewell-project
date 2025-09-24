"""
Medical Knowledge Search Engine

Provides semantic search capabilities for medical content with citation support
and calculator-specific filtering for evidence-based health risk assessment.
"""

import os
import sys
import weaviate
from pathlib import Path
import weaviate.classes as wvc
from typing import Dict, List, Optional
from dataclasses import dataclass, field 
from .config import WEAVIATE_HTTP_PORT, WEAVIATE_GRPC_PORT 

@dataclass
class SearchResult:
    """Structured search result with medical metadata."""
    title: str
    content: str
    organization: Optional[str] = None
    journal: Optional[str] = None
    calculator_support: List[str] = field(default_factory=list) 

    citation: str = ""
    evidence_grade: Optional[str] = None
    publication_year: Optional[int] = None
    url: Optional[str] = None

class MedicalSearchEngine:
    """Medical content search with semantic capabilities."""
    
    def __init__(self):
        """Initialize search engine with Weaviate v4 connection."""
        self.client = weaviate.connect_to_local(port=WEAVIATE_HTTP_PORT, grpc_port=WEAVIATE_GRPC_PORT)
    
    def close(self):
        """Close Weaviate connection."""
        try:
            self.client.close()
        except Exception:
            pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()
    
    def check_connection(self) -> bool:
        """Verify Weaviate connectivity."""
        try:
            self.client.is_ready()
            return True
        except Exception as e:
            print(f" Search engine connection failed: {e}")
            return False
    
    def get_knowledge_base_stats(self) -> Dict[str, int]:
        stats = {}
        
        for collection_name in ["MedicalGuideline", "ResearchAbstract"]:
            try:
                collection = self.client.collections.get(collection_name)
                response = collection.aggregate.over_all(total_count=True)
                stats[collection_name] = response.total_count
            except Exception as e:
                print(f"Warning: Could not get count for {collection_name}: {e}")
                stats[collection_name] = 0
        
        return stats
    
    def search_medical_content(
        self, 
        query: str, 
        content_type: Optional[str] = None,
        calculator_filter: Optional[str] = None,
        limit: int = 5,
        search_method: str = "semantic"
    ) -> List[SearchResult]:
        """Search medical content with collection-specific property handling."""
        if not self.check_connection():
            return []
        
        target_collections = []
        if content_type:
            if content_type in ["MedicalGuideline", "ResearchAbstract"]:
                target_collections = [content_type]
            else:
                print(f"Warning: Invalid content_type '{content_type}', searching all types")
                target_collections = ["MedicalGuideline", "ResearchAbstract"]
        else:
            target_collections = ["MedicalGuideline", "ResearchAbstract"]
        
        all_results = []
        
        for collection_name in target_collections:
            try:
                collection = self.client.collections.get(collection_name)
                
                # Collection-specific property lists (prevents schema errors)
                if collection_name == "MedicalGuideline":
                    return_properties = [
                        "title", "content", "organization", "calculator_support",
                        "citation", "evidence_grade", "publication_year", "url", 
                        "medical_domain", "section", "page_reference"
                    ]
                else:  # ResearchAbstract
                    return_properties = [
                        "title", "content", "authors", "journal", "calculator_support",
                        "citation", "evidence_level", "publication_year", "pmid", 
                        "doi", "medical_domain", "study_type", "population_size"
                    ]
                
                # Build filter if calculator specified
                where_filter = None
                if calculator_filter:
                    where_filter = wvc.query.Filter.by_property("calculator_support").contains_any([calculator_filter])
                
                # Execute search based on method and query presence
                if (not query or query.strip() == "") and where_filter is not None:
                    # Filter-only retrieval for calculator-specific searches without text queries
                    response = collection.query.fetch_objects(
                        limit=limit,
                        return_properties=return_properties,
                        filters=where_filter
                    )
                elif search_method == "semantic" and query:
                    # Semantic search with optional filtering
                    response = collection.query.near_text(
                        query=query,
                        limit=limit,
                        return_properties=return_properties,
                        filters=where_filter
                    )
                else:
                    # BM25 keyword search with optional filtering
                    response = collection.query.bm25(
                        query=query if query else "*",
                        limit=limit,
                        return_properties=return_properties,
                        filters=where_filter
                    )
                
                # Process results with proper property handling
                for obj in response.objects:
                    props = obj.properties
                    result = SearchResult(
                        title=props.get('title', 'Untitled'),
                        content=props.get('content', ''),
                        organization=props.get('organization'),  # MedicalGuideline only
                        journal=props.get('journal'),            # ResearchAbstract only
                        calculator_support=props.get('calculator_support', []),
                        citation=props.get('citation', 'Citation not available'),
                        evidence_grade=props.get('evidence_grade') or props.get('evidence_level'),
                        publication_year=props.get('publication_year'),
                        url=props.get('url')  # MedicalGuideline only
                    )
                    all_results.append(result)
                
            except Exception as e:
                print(f"Error searching {collection_name}: {e}")
        
        return all_results[:limit]
    
    def search_by_calculator(self, calculator_name: str, limit: int = 10) -> List[SearchResult]:
        """Search for content supporting a specific calculator."""
        return self.search_medical_content(
            query="",
            calculator_filter=calculator_name,
            limit=limit,
            search_method="bm25"
        )

def main():
    """Command-line interface for search testing."""
    import sys
    
    with MedicalSearchEngine() as search_engine:
        if not search_engine.check_connection():
            print("Cannot connect to knowledge base. Ensure Weaviate is running.")
            return
        
        stats = search_engine.get_knowledge_base_stats()
        print(" Knowledge Base Statistics:")
        for class_name, count in stats.items():
            print(f"   {class_name}: {count} documents")
        
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            print(f"\n Searching for: '{query}'")
            results = search_engine.search_medical_content(query)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.title}")
                    if result.organization:
                        print(f"   Organization: {result.organization}")
                    elif result.journal:
                        print(f"   Journal: {result.journal}")
                    if result.calculator_support:
                        print(f"   Calculators: {', '.join(result.calculator_support)}")
                    print(f"   Citation: {result.citation[:100]}...")
            else:
                print("No results found.")

if __name__ == "__main__":
    main()
