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
            print(f" Weaviate connection failed: {e}")
            print(f"   Ensure Weaviate is running: docker ps")
            print(f"   Test connectivity: curl http://localhost:8080/v1/meta")
            return False
    
    def get_existing_collections(self) -> set:
        """Retrieve existing collection names."""
        try:
            collections = self.client.collections.list_all()
            return {collection.name for collection in collections.values()}
        except Exception as e:
            print(f" Error retrieving collections: {e}")
            return set()
    
    def create_medical_guideline_collection(self):
        """Create MedicalGuideline collection with v4 syntax."""
        properties = [
            # ... keep all your existing properties exactly the same ...
            wvc.Property(name="content_hash", data_type=wvc.DataType.TEXT, description="SHA256 of source file for idempotent upserts")
        ]
        
        self.client.collections.create(
            name="MedicalGuideline",
            description="Clinical guidelines from major medical organizations with complete citation metadata",
            properties=properties,
            vector_config=wvc.Configure.NamedVectors(  # ✅ Use available NamedVectors
                default=wvc.Configure.VectorIndex(
                    vectorizer=wvc.Configure.Vectorizer.text2vec_transformers()
                )
            )
        )

    def create_research_abstract_collection(self):
        """Create ResearchAbstract collection with v4 syntax."""
        properties = [
            # ... keep all your existing properties exactly the same ...
            wvc.Property(name="content_hash", data_type=wvc.DataType.TEXT, description="SHA256 of source file for idempotent upserts")
        ]
        
        self.client.collections.create(
            name="ResearchAbstract",
            description="Peer-reviewed medical research abstracts with complete bibliographic metadata",
            properties=properties,
            vector_config=wvc.Configure.NamedVectors(
                default=wvc.Configure.VectorIndex(
                    vectorizer=wvc.Configure.Vectorizer.text2vec_transformers()
                )
            )
        )
    
    def setup_complete_schema(self) -> bool:
        """Create complete medical content schema with idempotent behavior."""
        print("  Setting up SourceWell Medical Knowledge Base Schema (v4)")
        print("=" * 60)
        
        if not self.check_weaviate_connection():
            return False
        
        existing_collections = self.get_existing_collections()
        success = True
        
        # Create MedicalGuideline collection
        if "MedicalGuideline" not in existing_collections:
            try:
                self.create_medical_guideline_collection()
                print(" MedicalGuideline collection created successfully")
            except Exception as e:
                print(f" Error creating MedicalGuideline collection: {e}")
                success = False
        else:
            print(" MedicalGuideline collection already exists")
        
        # Create ResearchAbstract collection
        if "ResearchAbstract" not in existing_collections:
            try:
                self.create_research_abstract_collection()
                print(" ResearchAbstract collection created successfully")
            except Exception as e:
                print(f" Error creating ResearchAbstract collection: {e}")
                success = False
        else:
            print(" ResearchAbstract collection already exists")
        
        if success:
            print("\n SourceWell Medical Knowledge Base schema setup complete!")
            print("   Ready for medical content ingestion and semantic search.")
        else:
            print("\n Schema setup encountered errors. Check Weaviate status.")
        
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
                print(" Weaviate connection successful")
            else:
                print(" Weaviate connection failed")
        elif command == "reset":
            print("  WARNING: This will delete all data!")
            confirm = input("Type 'RESET' to confirm: ")
            if confirm == "RESET":
                try:
                    existing = manager.get_existing_collections()
                    for collection_name in ["MedicalGuideline", "ResearchAbstract"]:
                        if collection_name in existing:
                            manager.client.collections.delete(collection_name)
                            print(f" Deleted collection: {collection_name}")
                    print(" Schema reset complete.")
                except Exception as e:
                    print(f" Error resetting schema: {e}")
            else:
                print("Reset cancelled.")
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
