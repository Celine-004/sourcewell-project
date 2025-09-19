# infrastructure_test.py
import weaviate
import json
import sys
from typing import Dict, List, Any

def test_weaviate_connection():
    """Test basic Weaviate connectivity and module availability."""
    print("=== Testing Weaviate Connection ===")
    
    try:
        client = weaviate.connect_to_local(port=8080, grpc_port=50051)
        
        if not client.is_ready():
            print(" Failed to connect to Weaviate")
            return False
            
        print(" Successfully connected to Weaviate")
        
        # Check if required collections exist
        collections = client.collections.list_all()
        collection_names = [col.name for col in collections.values()]
        
        required_collections = ["MedicalGuideline", "ResearchAbstract"]
        for col_name in required_collections:
            if col_name in collection_names:
                print(f" Collection '{col_name}' exists")
            else:
                print(f" Collection '{col_name}' missing")
                return False
        
        client.close()
        return True
        
    except Exception as e:
        print(f" Connection error: {e}")
        return False

def test_content_counts():
    """Verify medical content has been ingested properly."""
    print("\n=== Testing Content Counts ===")
    
    try:
        client = weaviate.connect_to_local(port=8080, grpc_port=50051)
        
        # Check MedicalGuideline count
        mg_collection = client.collections.get("MedicalGuideline")
        mg_count = mg_collection.aggregate.over_all(total_count=True).total_count
        print(f" MedicalGuideline objects: {mg_count}")
        
        # Check ResearchAbstract count  
        ra_collection = client.collections.get("ResearchAbstract")
        ra_count = ra_collection.aggregate.over_all(total_count=True).total_count
        print(f" ResearchAbstract objects: {ra_count}")
        
        client.close()
        
        if mg_count == 0 and ra_count == 0:
            print(" No content found - you may need to run content ingestion")
            return False
            
        return True
        
    except Exception as e:
        print(f" Content count error: {e}")
        return False

def test_semantic_search():
    """Test semantic search functionality with medical queries."""
    print("\n=== Testing Semantic Search ===")
    
    try:
        client = weaviate.connect_to_local(port=8080, grpc_port=50051)
        
        # Test semantic search on MedicalGuideline
        mg_collection = client.collections.get("MedicalGuideline")
        response = mg_collection.query.near_text(
            query="diabetes risk assessment prevention",
            limit=3,
            return_properties=["title", "organization", "publication_year"]
        )
        
        if response.objects:
            print(f" Semantic search returned {len(response.objects)} results")
            for i, obj in enumerate(response.objects, 1):
                title = obj.properties.get('title', 'No title')[:50]
                org = obj.properties.get('organization', 'Unknown')
                print(f"  {i}. {title}... ({org})")
        else:
            print(" Semantic search returned no results")
            client.close()
            return False
            
        client.close()
        return True
        
    except Exception as e:
        print(f" Semantic search error: {e}")
        return False

def test_calculator_metadata():
    """Verify calculator metadata is properly configured."""
    print("\n=== Testing Calculator Metadata ===")
    
    try:
        client = weaviate.connect_to_local(port=8080, grpc_port=50051)
        
        expected_calculators = ["FINDRISC", "ModifiedFramingham", "ColorectalScreening"]
        found_calculators = set()
        
        # Check MedicalGuideline calculator support
        mg_collection = client.collections.get("MedicalGuideline")
        
        for calc in expected_calculators:
            response = mg_collection.query.fetch_objects(
                filters=weaviate.classes.query.Filter.by_property("calculator_support").contains_any([calc]),
                limit=1,
                return_properties=["title", "calculator_support"]
            )
            
            if response.objects:
                found_calculators.add(calc)
                calc_support = response.objects[0].properties.get('calculator_support', [])
                print(f" {calc}: Found content with support {calc_support}")
            else:
                print(f" {calc}: No supporting content found")
        
        client.close()
        
        if len(found_calculators) == 0:
            print(" No calculator metadata found - check ingestion")
            return False
            
        return True
        
    except Exception as e:
        print(f" Calculator metadata error: {e}")
        return False

def test_citation_format():
    """Verify citations are properly formatted."""
    print("\n=== Testing Citation Format ===")
    
    try:
        client = weaviate.connect_to_local(port=8080, grpc_port=50051)
        
        # Get a sample object to check citation format
        mg_collection = client.collections.get("MedicalGuideline")
        response = mg_collection.query.fetch_objects(
            limit=1,
            return_properties=["title", "citation"]
        )
        
        if response.objects:
            citation = response.objects[0].properties.get('citation', '')
            title = response.objects[0].properties.get('title', 'Unknown')[:30]
            
            if citation and ('Available from:' in citation or 'doi:' in citation):
                print(f" Citation format validated for: {title}...")
                print(f"   Citation: {citation[:80]}...")
            else:
                print(f" Citation format issue for: {title}...")
                return False
        else:
            print(" No objects found for citation testing")
            return False
            
        client.close()
        return True
        
    except Exception as e:
        print(f" Citation format error: {e}")
        return False

def main():
    """Run comprehensive infrastructure test suite."""
    print(" SourceWell Infrastructure Test Suite")
    print("=" * 50)
    
    tests = [
        ("Weaviate Connection", test_weaviate_connection),
        ("Content Counts", test_content_counts),
        ("Semantic Search", test_semantic_search),
        ("Calculator Metadata", test_calculator_metadata),
        ("Citation Format", test_citation_format)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n Test '{test_name}' failed - see output above")
    
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print(" All tests passed! Infrastructure is ready for calculator development.")
        return 0
    else:
        print(" Some tests failed. Please address issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

