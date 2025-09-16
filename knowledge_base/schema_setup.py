import weaviate
import os

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
client = weaviate.Client(WEAVIATE_URL)

def create_medical_schema():
    """Create schema classes for medical content with semantic search capabilities."""
    
    medical_guideline_class = {
        "class": "MedicalGuideline",
        "description": "Clinical guidelines from major medical organizations",
        "vectorizer": "text2vec-transformers",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "organization", "dataType": ["text"]},
            {"name": "title", "dataType": ["text"]},
            {"name": "publication_year", "dataType": ["int"]},
            {"name": "section", "dataType": ["text"]},
            {"name": "evidence_grade", "dataType": ["text"]},
            {"name": "url", "dataType": ["text"]},
            {"name": "calculator_support", "dataType": ["text[]"]},
            {"name": "medical_domain", "dataType": ["text[]"]},
            {"name": "page_reference", "dataType": ["text"]},
            {"name": "accessed_date", "dataType": ["text"]},
            {"name": "review_status", "dataType": ["text"]},
            {"name": "pmid", "dataType": ["text"]},
            {"name": "doi", "dataType": ["text"]},
            {"name": "citation", "dataType": ["text"]}
        ],
        "moduleConfig": {
            "text2vec-transformers": {
                "vectorizeClassName": False,
                "poolingStrategy": "mean"
            }
        }
    }

    research_abstract_class = {
        "class": "ResearchAbstract",
        "description": "Peer-reviewed medical research abstracts",
        "vectorizer": "text2vec-transformers",
        "properties": [
            {"name": "content", "dataType": ["text"]},
            {"name": "title", "dataType": ["text"]},
            {"name": "authors", "dataType": ["text[]"]},
            {"name": "journal", "dataType": ["text"]},
            {"name": "publication_year", "dataType": ["int"]},
            {"name": "pmid", "dataType": ["text"]},
            {"name": "doi", "dataType": ["text"]},
            {"name": "study_type", "dataType": ["text"]},
            {"name": "population_size", "dataType": ["text"]},
            {"name": "calculator_support", "dataType": ["text[]"]},
            {"name": "medical_domain", "dataType": ["text[]"]},
            {"name": "evidence_level", "dataType": ["text"]},
            {"name": "accessed_date", "dataType": ["text"]},
            {"name": "review_status", "dataType": ["text"]},
            {"name": "citation", "dataType": ["text"]}
        ],
        "moduleConfig": {
            "text2vec-transformers": {
                "vectorizeClassName": False,
                "poolingStrategy": "mean"
            }
        }
    }

    # Create classes if they don't exist
    try:
        schema = client.schema.get()
        existing_classes = {cls["class"] for cls in schema.get("classes", [])}

        if "MedicalGuideline" not in existing_classes:
            client.schema.create_class(medical_guideline_class)
            print("✓ MedicalGuideline class created successfully")
        else:
            print("✓ MedicalGuideline class already exists")

        if "ResearchAbstract" not in existing_classes:
            client.schema.create_class(research_abstract_class)
            print("✓ ResearchAbstract class created successfully")
        else:
            print("✓ ResearchAbstract class already exists")
            
        print("\n🎉 Weaviate schema setup complete!")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        print("Troubleshooting:")
        print("1. Ensure Weaviate is running: docker ps")
        print("2. Test API: curl http://localhost:8080/v1/meta")

if __name__ == "__main__":
    create_medical_schema()