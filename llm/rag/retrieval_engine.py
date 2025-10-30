"""
Retrieval Engine for RAG System
Integrates with existing knowledge base
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Import existing knowledge base
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from knowledge_base.search_engine import MedicalSearchEngine
from knowledge_base import config as kb_config

class RetrievalEngine:
    """Handles document retrieval for RAG system"""
    
    def __init__(self):
        self.search_engine = None
        self.logger = logging.getLogger(__name__)
        
        # Retrieval parameters
        self.default_limit = 5
        self.min_relevance_threshold = 0.3
            
    def _ensure_search_engine(self):
        """Ensure search engine is initialized"""
        if self.search_engine is None:
            try:
                from knowledge_base.search_engine import MedicalSearchEngine
                self.search_engine = MedicalSearchEngine()
                
                # Test the search engine is actually working
                try:
                    # Do a simple test search
                    test_results = self.search_engine.search_medical_content(
                        query="diabetes",
                        limit=1,
                        search_method="bm25"
                    )
                    self.logger.info("Search engine initialized and tested successfully")
                    return True
                except Exception as test_error:
                    self.logger.warning(f"Search engine test failed: {test_error}")
                    # Continue anyway - search might still work for other queries
                    return True
                    
            except Exception as e:
                self.logger.error(f"Failed to initialize search engine: {e}")
                self.search_engine = None
                return False
        return True
        
    def retrieve_context(
        self,
        patient_data: Dict[str, Any],
        risk_results: Dict[str, Any],
        explanation_type: str = "general",
        limit: int = None
    ) -> Dict[str, Any]:
        """Retrieve relevant context for explanation generation"""
        
        # Initialize default return structure
        default_return = {
            'success': False,
            'error': 'Unknown error',
            'sources': [],
            'context': 'Based on medical guidelines and evidence-based practices.'
        }
        
        try:
            # Ensure search engine is available
            if not self._ensure_search_engine():
                return {
                    'success': False,
                    'error': 'Search engine unavailable',
                    'sources': [],
                    'context': 'Based on medical guidelines and evidence-based practices.'
                }
            
            limit = limit or self.default_limit
            
            # Build search queries based on results
            queries = self._build_search_queries(patient_data, risk_results, explanation_type)
            
            all_sources = []
            used_queries = []
            
            for query in queries:
                if query:  # Skip empty queries
                    sources = self._search_knowledge_base(query, limit=3)
                    if sources:
                        all_sources.extend(sources)
                        used_queries.append(query)
            
            # If no sources found, return with default context
            if not all_sources:
                return {
                    'success': True,  # Not an error, just no results
                    'sources': [],
                    'context': 'Based on medical guidelines and evidence-based practices.',
                    'queries': used_queries,
                    'total_found': 0,
                    'after_dedup': 0,
                    'source_count': 0
                }
            
            # Remove duplicates and rank by relevance
            unique_sources = self._deduplicate_sources(all_sources)
            ranked_sources = self._rank_sources(unique_sources, patient_data, risk_results)
            
            # Limit final results
            final_sources = ranked_sources[:limit]
            
            # Build context from sources
            context_parts = []
            for source in final_sources:
                content = source.get('content', '')
                if content:
                    context_parts.append(content)
            
            return {
                'success': True,
                'sources': final_sources,
                'context': '\n\n'.join(context_parts) if context_parts else 'Based on medical guidelines and evidence-based practices.',
                'queries': used_queries,
                'total_found': len(all_sources),
                'after_dedup': len(unique_sources),
                'source_count': len(final_sources)
            }
            
        except Exception as e:
            self.logger.error(f"Retrieval failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'sources': [],
                'context': 'Based on medical guidelines and evidence-based practices.'
            }
    
    def _build_search_queries(
        self,
        patient_data: Dict[str, Any],
        risk_results: Dict[str, Any],
        explanation_type: str
    ) -> List[str]:
        """Build targeted search queries based on patient data and results"""
        
        queries = []
        
        # Base queries by explanation type
        if explanation_type == "diabetes" or "findrisc" in risk_results:
            queries.extend([
                "diabetes risk factors prevention",
                "FINDRISC diabetes screening",
                "type 2 diabetes prevention lifestyle"
            ])
        
        if explanation_type == "cardiovascular" or "framingham" in risk_results:
            queries.extend([
                "cardiovascular disease prevention",
                "Framingham risk score guidelines",
                "heart disease risk factors"
            ])
        
        if explanation_type == "colorectal" or "colorectal" in risk_results:
            queries.extend([
                "colorectal cancer screening guidelines",
                "colon cancer prevention",
                "USPSTF colorectal screening"
            ])
        
        # Add risk-factor specific queries
        risk_queries = self._build_risk_factor_queries(patient_data)
        queries.extend(risk_queries)
        
        # Add result-specific queries
        result_queries = self._build_result_specific_queries(risk_results)
        queries.extend(result_queries)
        
        return list(set(queries))  # Remove duplicates
    
    def _build_risk_factor_queries(self, patient_data: Dict[str, Any]) -> List[str]:
        """Build queries based on patient risk factors"""
        queries = []
        
        # Smoking
        if patient_data.get('current_smoker'):
            queries.append("smoking cessation cardiovascular diabetes")
        
        # Blood pressure
        if patient_data.get('hypertension_medication') or (
            patient_data.get('systolic_bp', 0) > 130 or patient_data.get('diastolic_bp', 0) > 80
        ):
            queries.append("hypertension blood pressure management")
        
        # BMI/Weight
        bmi = patient_data.get('bmi')
        if bmi and bmi >= 30:
            queries.append("obesity weight management health risks")
        elif bmi and bmi >= 25:
            queries.append("overweight weight loss prevention")
        
        # Family history
        if patient_data.get('family_diabetes_history', 'none') != 'none':
            queries.append("family history diabetes genetic risk")
            
    def _build_risk_factor_queries(self, patient_data: Dict[str, Any]) -> List[str]:
        """Build queries based on patient risk factors"""
        queries = []
        
        # Ensure patient_data is a dict
        if not isinstance(patient_data, dict):
            return queries
        
        # Smoking
        if patient_data.get('current_smoker'):
            queries.append("smoking cessation cardiovascular diabetes")
        
        # Blood pressure
        if patient_data.get('hypertension_medication') or (
            patient_data.get('systolic_bp', 0) > 130 or patient_data.get('diastolic_bp', 0) > 80
        ):
            queries.append("hypertension blood pressure management")
        
        # BMI/Weight
        bmi = patient_data.get('bmi')
        if bmi and isinstance(bmi, (int, float)):
            if bmi >= 30:
                queries.append("obesity weight management health risks")
            elif bmi >= 25:
                queries.append("overweight weight loss prevention")
        
        # Family history
        family_diabetes = patient_data.get('family_diabetes_history', 'none')
        if family_diabetes and family_diabetes != 'none':
            queries.append("family history diabetes genetic risk")
        
        if patient_data.get('family_colorectal_cancer'):
            queries.append("family history colorectal cancer screening")
        
        # Cholesterol
        total_chol = patient_data.get('total_cholesterol', 0)
        if isinstance(total_chol, (int, float)) and total_chol > 240:
            queries.append("high cholesterol management guidelines")
        
        return queries
    
    def _build_result_specific_queries(self, risk_results: Dict[str, Any]) -> List[str]:
        """Build queries based on specific risk calculation results"""
        queries = []
        
        # Handle different possible structures of risk_results
        if not isinstance(risk_results, dict):
            return queries
        
        # Check if it's wrapped in a 'results' key
        if 'results' in risk_results:
            calc_results = risk_results.get('results', {})
        else:
            calc_results = risk_results
        
        for calc_name, result in calc_results.items():
            # Skip if result is None, bool, or error dict
            if result is None or isinstance(result, bool):
                continue
                
            # Handle error results
            if isinstance(result, dict) and 'error' in result:
                continue
            
            # Handle object results (from actual calculators)
            if hasattr(result, 'ten_year_risk_percentage'):
                # It's a result object from calculators
                if calc_name in ['findrisc', 'diabetes']:
                    if hasattr(result, 'total_score'):
                        score = result.total_score
                        if score >= 15:  # High risk
                            queries.append("high diabetes risk prevention interventions")
                        elif score >= 12:  # Moderate risk
                            queries.append("prediabetes lifestyle modification")
                
                elif calc_name in ['framingham', 'cardiovascular']:
                    risk_pct = result.ten_year_risk_percentage
                    if risk_pct >= 20:  # High risk
                        queries.append("high cardiovascular risk treatment statin")
                    elif risk_pct >= 7.5:  # Intermediate risk
                        queries.append("intermediate cardiovascular risk assessment")
            
            # Handle dict results (legacy format)
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('result', {})
                
                if calc_name == 'findrisc':
                    score = data.get('score', 0)
                    if score >= 15:
                        queries.append("high diabetes risk prevention interventions")
                    elif score >= 12:
                        queries.append("prediabetes lifestyle modification")
                
                elif calc_name == 'framingham':
                    risk_pct = data.get('ten_year_risk_percentage', 0)
                    if risk_pct >= 20:
                        queries.append("high cardiovascular risk treatment statin")
                    elif risk_pct >= 7.5:
                        queries.append("intermediate cardiovascular risk assessment")
            
            # Handle colorectal results
            if calc_name in ['colorectal', 'colorectal_screening']:
                if hasattr(result, 'risk_level'):
                    risk_level = result.risk_level
                    if risk_level and 'high' in str(risk_level).lower():
                        queries.append("high risk colorectal screening enhanced")
                elif isinstance(result, dict):
                    risk_level = result.get('risk_level', 'average')
                    if 'high' in risk_level.lower():
                        queries.append("high risk colorectal screening enhanced")
        
        return queries
    
    def _search_knowledge_base(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the knowledge base with a specific query"""
        try:
            if self.search_engine:
                # Try semantic search first
                try:
                    results = self.search_engine.search_medical_content(
                        query=query,
                        limit=limit,
                        search_method="semantic"
                    )
                except Exception as e:
                    self.logger.debug(f"Semantic search failed: {e}, trying keyword search")
                    results = None
                
                # If semantic failed or no results, try keyword
                if not results:
                    try:
                        results = self.search_engine.search_medical_content(
                            query=query,
                            limit=limit,
                            search_method="bm25"
                        )
                    except Exception as e:
                        self.logger.debug(f"Keyword search also failed: {e}")
                        return []
                
                return [self._format_search_result(result) for result in results] if results else []
            else:
                self.logger.error("Search engine not available")
                return []
                
        except Exception as e:
            self.logger.error(f"Knowledge base search failed for '{query}': {e}")
            return []
    
    def _format_search_result(self, result) -> Dict[str, Any]:
        """Format search result for use in prompts"""
        return {
            "title": getattr(result, 'title', 'Unknown'),
            "content": getattr(result, 'content', ''),
            "organization": getattr(result, 'organization', 'Unknown'),
            "journal": getattr(result, 'journal', ''),
            "citation": getattr(result, 'citation', ''),
            "evidence_grade": getattr(result, 'evidence_grade', ''),
            "publication_year": getattr(result, 'publication_year', ''),
            "url": getattr(result, 'url', ''),
            "calculator_support": getattr(result, 'calculator_support', [])
        }
    
    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on title and content similarity"""
        seen_titles = set()
        unique_sources = []
        
        for source in sources:
            title = source.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_sources.append(source)
        
        return unique_sources
    
    def _rank_sources(
        self,
        sources: List[Dict[str, Any]],
        patient_data: Dict[str, Any],
        risk_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank sources by relevance to patient context"""
        
        def calculate_relevance_score(source: Dict[str, Any]) -> float:
            score = 1.0  # Base score
            
            # Boost based on calculator support
            calculator_support = source.get('calculator_support', [])
            for calc in risk_results.keys():
                if calc in calculator_support:
                    score += 0.3
            
            # Boost based on evidence quality
            evidence_grade = source.get('evidence_grade', '').upper()
            if evidence_grade in ['A', 'I']:
                score += 0.2
            elif evidence_grade in ['B', 'II']:
                score += 0.1
            
            # Boost recent publications
            pub_year = source.get('publication_year')
            if pub_year:
                try:
                    year = int(pub_year)
                    if year >= 2020:
                        score += 0.2
                    elif year >= 2015:
                        score += 0.1
                except:
                    pass
            
            # Boost authoritative organizations
            org = source.get('organization', '').lower()
            authoritative_orgs = ['ada', 'aha', 'acc', 'uspstf', 'who', 'cdc']
            if any(auth_org in org for auth_org in authoritative_orgs):
                score += 0.2
            
            return score
        
        # Calculate scores and sort
        scored_sources = []
        for source in sources:
            score = calculate_relevance_score(source)
            scored_sources.append((score, source))
        
        # Sort by score (descending)
        scored_sources.sort(key=lambda x: x[0], reverse=True)
        
        return [source for score, source in scored_sources]
    
    def get_calculator_specific_context(self, calculator_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get context specific to a calculator"""
        if not self._ensure_search_engine():
            return []
        
        try:
            with self.search_engine:
                results = self.search_engine.search_by_calculator(
                    calculator_name=calculator_name,
                    limit=limit
                )
                
                return [self._format_search_result(result) for result in results]
                
        except Exception as e:
            self.logger.error(f"Calculator-specific search failed for '{calculator_name}': {e}")
            return []
    def retrieve_context_simple(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Simple retrieval method for basic query strings"""
        
        if not self._ensure_search_engine():
            return {
                'success': False,
                'error': 'Search engine unavailable',
                'sources': [],
                'context': ''
            }
        
        try:
            # Search knowledge base
            sources = self._search_knowledge_base(query, limit=limit)
            
            if not sources:
                return {
                    'success': True,
                    'sources': [],
                    'context': 'No relevant medical information found in knowledge base.',
                    'source_count': 0
                }
            
            # Format context from sources
            context_parts = []
            for source in sources:
                content = source.get('content', '')
                if content:
                    context_parts.append(content)
            
            return {
                'success': True,
                'sources': sources,
                'context': '\n\n'.join(context_parts),
                'source_count': len(sources)
            }
            
        except Exception as e:
            self.logger.error(f"Simple retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'sources': [],
                'context': ''
            }