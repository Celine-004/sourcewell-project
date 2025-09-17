class MedicalSearchEngine:
    """Professional medical content search with semantic capabilities."""
    
    def __init__(self):
        """Initialize search engine with Weaviate v4 connection."""
        self.client = weaviate.connect_to_local(port=8080, grpc_port=50051)
    
    def close(self):
        """Close Weaviate connection."""
        try:
            self.client.close()
        except Exception:
            pass
    
    def check_connection(self) -> bool:
        """Verify Weaviate connectivity."""
        try:
            self.client.is_ready()
            return True
        except Exception as e:
            print(f"❌ Search engine connection failed: {e}")
            return False
    
    def get_knowledge_base_stats(self) -> Dict[str, int]:
        """Get statistics about the knowledge base content."""
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
        """Search medical content with multiple filtering options."""
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
        
        return_properties = [
            "title", "content", "organization", "journal", "calculator_support",
            "citation", "evidence_grade", "publication_year", "url", "medical_domain"
        ]
        
        all_results = []
        
        for collection_name in target_collections:
            try:
                collection = self.client.collections.get(collection_name)
                
                # Build filter if calculator specified
                where_filter = None
                if calculator_filter:
                    where_filter = weaviate.classes.query.Filter.by_property("calculator_support").contains_any([calculator_filter])
                
                # Execute search based on method
                if search_method == "semantic" and query:
                    response = collection.query.near_text(
                        query=query,
                        limit=limit,
                        return_properties=return_properties,
                        where=where_filter
                    )
                else:
                    response = collection.query.bm25(
                        query=query if query else "*",
                        limit=limit,
                        return_properties=return_properties,
                        where=where_filter
                    )
                
                # Process results
                for obj in response.objects:
                    props = obj.properties
                    result = SearchResult(
                        title=props.get('title', 'Untitled'),
                        content=props.get('content', ''),
                        organization=props.get('organization'),
                        journal=props.get('journal'),
                        calculator_support=props.get('calculator_support', []),
                        citation=props.get('citation', 'Citation not available'),
                        evidence_grade=props.get('evidence_grade'),
                        publication_year=props.get('publication_year'),
                        url=props.get('url')
                    )
                    all_results.append(result)
                
            except Exception as e:
                print(f"Error searching {collection_name}: {e}")
        
        return all_results[:limit]
