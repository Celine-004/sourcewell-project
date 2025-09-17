"""
Medical Database Schema Management (Weaviate v4)

Creates and manages Weaviate collections for clinical guidelines and research
abstracts with complete metadata support for citation verification and semantic search.
"""

import weaviate
import weaviate.classes.config as wvc
from typing import Dict, List, Optional

class MedicalSchemaManager:
    """Manages Weaviate schema for medical content with clinical-grade metadata."""
    
    def __init__(self):
        """Initialize schema manager with Weaviate v4 connection."""
        self.client = weaviate.connect_to_local(port=8080, grpc_port=50051)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.client.close()
    
    def check_weaviate_connection(self) -> bool:
        """Verify Weaviate server connectivity."""
        try:
            self.client.is_ready()
            return True
        except Exception as e:
            print(f"❌ Weaviate connection failed: {e}")
            print(f"   Ensure Weaviate is running: docker ps")
            print(f"   Test connectivity: curl http://localhost:8080/v1/meta")
            return False
    
    def get_existing_collections(self) -> set:
        """Retrieve existing collection names."""
        try:
            collections = self.client.collections.list_all()
            return {collection.name for collection in collections.values()}
        except Exception as e:
            print(f"❌ Error retrieving collections: {e}")
            return set()
    
    def create_medical_guideline_collection(self):
        """Create MedicalGuideline collection with v4 syntax."""
        properties = [
            wvc.Property(name="content", data_type=wvc.DataType.TEXT, description="Extracted medical content"),
            wvc.Property(name="organization", data_type=wvc.DataType.TEXT, description="Publishing medical organization"),
            wvc.Property(name="title", data_type=wvc.DataType.TEXT, description="Official guideline title"),
            wvc.Property(name="publication_year", data_type=wvc.DataType.INT, description="Year of publication"),
            wvc.Property(name="section", data_type=wvc.DataType.TEXT, description="Hierarchical section path"),
            wvc.Property(name="evidence_grade", data_type=wvc.DataType.TEXT, description="Evidence quality grade"),
            wvc.Property(name="url", data_type=wvc.DataType.TEXT, description="Source URL for verification"),
            wvc.Property(name="calculator_support", data_type=wvc.DataType.TEXT_ARRAY, description="Supported risk calculators"),
            wvc.Property(name="medical_domain", data_type=wvc.DataType.TEXT_ARRAY, description="Medical specialty domains"),
            wvc.Property(name="page_reference", data_type=wvc.DataType.TEXT, description="Specific page or table reference"),
            wvc.Property(name="accessed_date", data_type=wvc.DataType.TEXT, description="Date content was accessed"),
            wvc.Property(name="review_status", data_type=wvc.DataType.TEXT, description="Quality review status"),
            wvc.Property(name="pmid", data_type=wvc.DataType.TEXT, description="PubMed ID if applicable"),
            wvc.Property(name="doi", data_type=wvc.DataType.TEXT, description="Digital Object Identifier"),
            wvc.Property(name="citation", data_type=wvc.DataType.TEXT, description="Vancouver-style citation")
        ]
        
        self.client.collections.create(
            name="MedicalGuideline",
            description="Clinical guidelines from major medical organizations with complete citation metadata",
            properties=properties,
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers()
        )
    
    def create_research_abstract_collection(self):
        """Create ResearchAbstract collection with v4 syntax."""
        properties = [
            wvc.Property(name="content", data_type=wvc.DataType.TEXT, description="Abstract content"),
            wvc.Property(name="title", data_type=wvc.DataType.TEXT, description="Research paper title"),
            wvc.Property(name="authors", data_type=wvc.DataType.TEXT_ARRAY, description="Author list"),
            wvc.Property(name="journal", data_type=wvc.DataType.TEXT, description="Publishing journal"),
            wvc.Property(name="publication_year", data_type=wvc.DataType.INT, description="Year of publication"),
            wvc.Property(name="pmid", data_type=wvc.DataType.TEXT, description="PubMed ID"),
            wvc.Property(name="doi", data_type=wvc.DataType.TEXT, description="Digital Object Identifier"),
            wvc.Property(name="study_type", data_type=wvc.DataType.TEXT, description="Type of research study"),
            wvc.Property(name="population_size", data_type=wvc.DataType.TEXT, description="Study population size"),
            wvc.Property(name="calculator_support", data_type=wvc.DataType.TEXT_ARRAY, description="Supported risk calculators"),
            wvc.Property(name="medical_domain", data_type=wvc.DataType.TEXT_ARRAY, description="Medical specialty domains"),
            wvc.Property(name="evidence_level", data_type=wvc.DataType.TEXT, description="Research evidence level"),
            wvc.Property(name="accessed_date", data_type=wvc.DataType.TEXT, description="Date content was accessed"),
            wvc.Property(name="review_status", data_type=wvc.DataType.TEXT, description="Quality review status"),
            wvc.Property(name="citation", data_type=wvc.DataType.TEXT, description="Vancouver-style citation")
        ]
        
        self.client.collections.create(
            name="ResearchAbstract",
            description="Peer-reviewed medical research abstracts with complete bibliographic metadata",
            properties=properties,
            vectorizer_config=wvc.Configure.Vectorizer.text2vec_transformers()
        )
    
    def setup_complete_schema(self) -> bool:
        """Create complete medical content schema with idempotent behavior."""
        print("🏗️  Setting up SourceWell Medical Knowledge Base Schema (v4)")
        print("=" * 60)
        
        if not self.check_weaviate_connection():
            return False
        
        existing_collections = self.get_existing_collections()
        success = True
        
        # Create MedicalGuideline collection
        if "MedicalGuideline" not in existing_collections:
            try:
                self.create_medical_guideline_collection()
                print("✓ MedicalGuideline collection created successfully")
            except Exception as e:
                print(f"❌ Error creating MedicalGuideline collection: {e}")
                success = False
        else:
            print("✓ MedicalGuideline collection already exists")
        
        # Create ResearchAbstract collection
        if "ResearchAbstract" not in existing_collections:
            try:
                self.create_research_abstract_collection()
                print("✓ ResearchAbstract collection created successfully")
            except Exception as e:
                print(f"❌ Error creating ResearchAbstract collection: {e}")
                success = False
        else:
            print("✓ ResearchAbstract collection already exists")
        
        if success:
            print("\n🎉 SourceWell Medical Knowledge Base schema setup complete!")
            print("   Ready for medical content ingestion and semantic search.")
        else:
            print("\n❌ Schema setup encountered errors. Check Weaviate status.")
        
        return success

def main():
    """Command-line interface for schema management."""
    import sys
    
    with MedicalSchemaManager() as manager:
        if len(sys.argv) < 2:
            print("Usage: python schema_setup.py [setup|check|reset]")
            print("  setup - Create complete medical content schema")
            print("  check - Verify Weaviate connectivity") 
            print("  reset - Delete all collections (destructive)")
            return
        
        command = sys.argv[1].lower()
        
        if command == "setup":
            manager.setup_complete_schema()
        elif command == "check":
            if manager.check_weaviate_connection():
                print("✓ Weaviate connection successful")
            else:
                print("❌ Weaviate connection failed")
        elif command == "reset":
            print("⚠️  WARNING: This will delete all data!")
            confirm = input("Type 'RESET' to confirm: ")
            if confirm == "RESET":
                try:
                    existing = manager.get_existing_collections()
                    for collection_name in ["MedicalGuideline", "ResearchAbstract"]:
                        if collection_name in existing:
                            manager.client.collections.delete(collection_name)
                            print(f"✓ Deleted collection: {collection_name}")
                    print("🔄 Schema reset complete.")
                except Exception as e:
                    print(f"❌ Error resetting schema: {e}")
            else:
                print("Reset cancelled.")
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
