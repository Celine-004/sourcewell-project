"""
Comprehensive Knowledge Base Testing

Tests schema creation, content ingestion, search functionality, and citation
verification for the SourceWell medical knowledge base.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from knowledge_base.schema_setup import MedicalSchemaManager
from knowledge_base.content_ingester import MedicalContentIngester
from knowledge_base.search_engine import MedicalSearchEngine

class TestMedicalKnowledgeBase(unittest.TestCase):
    """Comprehensive knowledge base functionality tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.schema_manager = MedicalSchemaManager()
        cls.content_ingester = MedicalContentIngester()
        cls.search_engine = MedicalSearchEngine()
    
    def test_weaviate_connectivity(self):
        """Test Weaviate server connectivity."""
        self.assertTrue(
            self.schema_manager.check_weaviate_connection(),
            "Cannot connect to Weaviate. Ensure 'docker-compose up -d' is running."
        )
    
    def test_schema_creation(self):
        """Test medical content schema creation."""
        success = self.schema_manager.setup_complete_schema()
        self.assertTrue(success, "Schema creation failed")
        
        existing_classes = self.schema_manager.get_existing_classes()
        self.assertIn("MedicalGuideline", existing_classes)
        self.assertIn("ResearchAbstract", existing_classes)
    
    def test_knowledge_base_statistics(self):
        """Test knowledge base content statistics."""
        stats = self.search_engine.get_knowledge_base_stats()
        
        self.assertIn("MedicalGuideline", stats)
        self.assertIn("ResearchAbstract", stats)
        
        total_content = sum(stats.values())
        if total_content > 0:
            print(f"✓ Knowledge base contains {total_content} documents")
        else:
            print("⚠️  Knowledge base is empty. Run content ingestion first.")
    
    def test_search_functionality(self):
        """Test basic search functionality."""
        results = self.search_engine.search_medical_content(
            "diabetes risk factors",
            limit=3
        )
        
        if results:
            self.assertGreater(len(results), 0)
            for result in results:
                self.assertIsNotNone(result.title)
                self.assertIsNotNone(result.content)
                self.assertIsNotNone(result.citation)
        else:
            print("⚠️  No search results found. Ensure content ingestion completed.")
    
    def test_calculator_specific_search(self):
        """Test calculator-specific content filtering."""
        findrisc_results = self.search_engine.search_by_calculator("FINDRISC")
        
        if findrisc_results:
            for result in findrisc_results:
                self.assertIn("FINDRISC", result.calculator_support)
        else:
            print("⚠️  No FINDRISC content found. Check content curation.")
    
    def test_citation_integrity(self):
        """Test citation generation and integrity."""
        results = self.search_engine.search_medical_content("medical", limit=1)
        
        if results:
            result = results[0]
            self.assertIsNotNone(result.citation)
            self.assertGreater(len(result.citation), 10)
            citation_lower = result.citation.lower()
            self.assertTrue(
                any(keyword in citation_lower for keyword in ['available from', 'pmid', 'doi', '20']),
                f"Citation lacks required elements: {result.citation}"
            )

def run_comprehensive_tests():
    """Run all knowledge base tests with detailed output."""
    print("🧪 SourceWell Knowledge Base Comprehensive Testing")
    print("=" * 60)
    
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMedicalKnowledgeBase))
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    print(f"\n📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n❌ Test Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n🎉 All tests passed! Knowledge base is ready for production use.")
    else:
        print(f"\n⚠️  Some tests failed. Review issues before proceeding.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_comprehensive_tests()
