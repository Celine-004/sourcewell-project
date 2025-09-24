import os
import sys
from pathlib import Path
import weaviate

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from knowledge_base.config import WEAVIATE_HTTP_PORT, WEAVIATE_GRPC_PORT

def inspect_calculator_support_data():
    """Inspect actual calculator_support data stored in Weaviate."""
    
    client = weaviate.connect_to_local(port=WEAVIATE_HTTP_PORT, grpc_port=WEAVIATE_GRPC_PORT)
    
    try:
        print("Calculator Support Data Inspection")
        print("=" * 55)
        
        for collection_name in ["MedicalGuideline", "ResearchAbstract"]:
            print(f"\n {collection_name} Collection:")
            print("-" * 30)
            
            try:
                collection = client.collections.get(collection_name)
                
                # Fetch all objects with title and calculator_support
                response = collection.query.fetch_objects(
                    return_properties=["title", "calculator_support"],
                    limit=50
                )
                
                if response.objects:
                    for i, obj in enumerate(response.objects, 1):
                        props = obj.properties
                        title = props.get('title', 'Untitled')
                        calc_support = props.get('calculator_support')
                        
                        print(f"{i:2d}. {title[:50]}")
                        print(f"    calculator_support: {calc_support}")
                        print(f"    Type: {type(calc_support)}")
                        if calc_support:
                            print(f"    Length: {len(calc_support)}")
                        print()
                else:
                    print(f"   No objects found in {collection_name}")
                    
            except Exception as e:
                print(f"    Error accessing {collection_name}: {e}")
        
        print(f"\n Expected Values for Matching:")
        print(f"   - Exact strings: 'FINDRISC', 'ModifiedFramingham', 'ColorectalScreening'")
        print(f"   - Format: ['FINDRISC'] or ['FINDRISC', 'ModifiedFramingham']")
        print(f"   - Case sensitive: Must match exactly")
        
    finally:
        client.close()

if __name__ == "__main__":
    inspect_calculator_support_data()
