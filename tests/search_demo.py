"""
Interactive Medical Search Demonstration

Demonstrates semantic search capabilities of the SourceWell medical knowledge
base with calculator-specific filtering and citation display.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from knowledge_base.search_engine import MedicalSearchEngine

def run_predefined_search_demo():
    """Run predefined search queries relevant to SourceWell calculators."""
    
    search_engine = MedicalSearchEngine()
    
    print("🔍 SourceWell Medical Knowledge Base Search Demonstration")
    print("=" * 65)
    
    if not search_engine.check_connection():
        print("❌ Cannot connect to knowledge base.")
        print("   Ensure Weaviate is running: docker-compose up -d")
        return False
    
    stats = search_engine.get_knowledge_base_stats()
    print("📊 Knowledge Base Statistics:")
    total_docs = sum(stats.values())
    for class_name, count in stats.items():
        print(f"   {class_name}: {count} documents")
    print(f"   Total: {total_docs} documents")
    
    if total_docs == 0:
        print("\n⚠️  Knowledge base is empty!")
        print("   Run: python knowledge_base/content_ingester.py")
        return False
    
    test_queries = [
        {
            "query": "diabetes risk factors",
            "description": "Diabetes risk assessment (FINDRISC support)",
            "content_type": "MedicalGuideline"
        },
        {
            "query": "FINDRISC validation study",
            "description": "Finnish Diabetes Risk Score validation",
            "content_type": "ResearchAbstract"
        },
        {
            "query": "blood pressure categories hypertension",
            "description": "Blood pressure classification (Framingham support)",
            "content_type": "MedicalGuideline"
        },
        {
            "query": "physical activity diabetes prevention",
            "description": "Physical activity recommendations",
            "content_type": None
        },
        {
            "query": "colorectal cancer screening age family history",
            "description": "Colorectal screening guidelines",
            "content_type": "MedicalGuideline"
        }
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n🔎 Search {i}: {test_query['description']}")
        print(f"   Query: '{test_query['query']}'")
        print(f"   Target: {test_query['content_type'] or 'All content types'}")
        print("-" * 50)
        
        try:
            results = search_engine.search_medical_content(
                query=test_query["query"],
                content_type=test_query["content_type"],
                limit=2
            )
            
            if results:
                for j, result in enumerate(results, 1):
                    print(f"\n   Result {j}: {result.title}")
                    
                    metadata_items = []
                    if result.organization:
                        metadata_items.append(f"Organization: {result.organization}")
                    elif result.journal:
                        metadata_items.append(f"Journal: {result.journal}")
                    
                    if result.publication_year:
                        metadata_items.append(f"Year: {result.publication_year}")
                    
                    if result.evidence_grade:
                        metadata_items.append(f"Evidence: {result.evidence_grade}")
                    
                    if result.calculator_support:
                        metadata_items.append(f"Calculators: {', '.join(result.calculator_support)}")
                    
                    if metadata_items:
                        print(f"   {' | '.join(metadata_items)}")
                    
                    content_preview = result.content[:150] + "..." if len(result.content) > 150 else result.content
                    print(f"   Content: {content_preview}")
                    
                    citation_preview = result.citation[:120] + "..." if len(result.citation) > 120 else result.citation
                    print(f"   Citation: {citation_preview}")
            else:
                print("   No results found.")
                
        except Exception as e:
            print(f"   ❌ Search error: {e}")
    
    return True

def run_calculator_specific_demo():
    """Demonstrate calculator-specific content filtering."""
    
    search_engine = MedicalSearchEngine()
    
    print(f"\n🧮 Calculator-Specific Content Demonstration")
    print("=" * 50)
    
    calculators = ["FINDRISC", "ModifiedFramingham", "ColorectalScreening"]
    
    for calculator in calculators:
        print(f"\n🔍 Content supporting {calculator}:")
        print("-" * 30)
        
        try:
            results = search_engine.search_by_calculator(calculator, limit=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.title}")
                    if result.organization:
                        print(f"   Source: {result.organization}")
                    elif result.journal:
                        print(f"   Journal: {result.journal}")
                    
                    content_snippet = result.content[:100] + "..." if len(result.content) > 100 else result.content
                    print(f"   Relevance: {content_snippet}")
            else:
                print(f"   No content found supporting {calculator}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main demonstration function."""
    
    success = run_predefined_search_demo()
    
    if success:
        run_calculator_specific_demo()
        print("\n🎉 Search demonstration complete!")
        print("   Knowledge base is ready for AI integration and risk calculator implementation.")
    else:
        print("\n⚠️  Search demonstration could not run.")
        print("   Ensure Weaviate is running and content has been ingested.")

if __name__ == "__main__":
    main()
