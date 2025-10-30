"""
Phi-3 Mini Local AI Engine
Integrates with existing knowledge base for RAG
"""
import torch
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

try:
    from llm.utils.citation_verifier import CitationVerifier
except ImportError:
    try:
        from .utils.citation_verifier import CitationVerifier
    except ImportError:
        try:
            from utils.citation_verifier import CitationVerifier
        except ImportError:
            logger.warning("CitationVerifier not available - verification will be disabled")
            CitationVerifier = None

class Phi3MiniEngine:
    """Local Phi-3 Mini inference engine with RAG capabilities"""
    
    def __init__(self, model_id: str = "microsoft/Phi-3-mini-4k-instruct"):
        """Initialize Phi3 Mini Engine with all components"""
        # Always set up logger first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize all attributes to None first
        self.model_wrapper = None
        self.retrieval_engine = None
        self.prompt_templates = None
        self.citation_verifier = None
        self._initialized = False
        
        # Generation settings
        self.default_generation_params = {
            "max_new_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.1
        }
        
        try:
            self.logger.info("Attempting to import LLM components...")
            
            current_dir = Path(__file__).parent
            engines_dir = current_dir / 'engines'
            rag_dir = current_dir / 'rag'
            utils_dir = current_dir / 'utils'
            
            if engines_dir.exists():
                sys.path.insert(0, str(current_dir))
            
            from llm.engines.phi3_wrapper import Phi3Wrapper
            from llm.rag.retrieval_engine import RetrievalEngine
            from llm.utils.prompt_templates import PromptTemplates
            
            self.logger.info("Successfully imported all components")
            
            self.model_wrapper = Phi3Wrapper(model_id)
            self.retrieval_engine = RetrievalEngine()
            self.prompt_templates = PromptTemplates()

            # ADD CITATION VERIFIER INITIALIZATION
            if CitationVerifier is not None:
                try:
                    self.citation_verifier = CitationVerifier()
                    self.logger.info("CitationVerifier initialized successfully")
                except Exception as e:
                    self.logger.warning(f"CitationVerifier initialization failed: {e}")
                    self.citation_verifier = None
            else:
                self.logger.warning("CitationVerifier class not available")
            
            self._initialized = True
            self.logger.info("Phi3MiniEngine components created successfully")
            
            self._initialized = True
            self.logger.info("Phi3MiniEngine components created successfully")
            
        except ImportError as e:
            self.logger.error(f"Failed to import required components: {e}")
            self.logger.info("Trying direct file import...")
            
            try:
                # Try direct file imports as fallback
                import importlib.util
                
                wrapper_path = Path(__file__).parent / 'engines' / 'phi3_wrapper.py'
                if wrapper_path.exists():
                    spec = importlib.util.spec_from_file_location("phi3_wrapper", wrapper_path)
                    phi3_wrapper_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(phi3_wrapper_module)
                    Phi3Wrapper = phi3_wrapper_module.Phi3Wrapper
                else:
                    raise ImportError(f"Cannot find {wrapper_path}")
                
                retrieval_path = Path(__file__).parent / 'rag' / 'retrieval_engine.py'
                if retrieval_path.exists():
                    spec = importlib.util.spec_from_file_location("retrieval_engine", retrieval_path)
                    retrieval_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(retrieval_module)
                    RetrievalEngine = retrieval_module.RetrievalEngine
                else:
                    raise ImportError(f"Cannot find {retrieval_path}")
                
                templates_path = Path(__file__).parent / 'utils' / 'prompt_templates.py'
                if templates_path.exists():
                    spec = importlib.util.spec_from_file_location("prompt_templates", templates_path)
                    templates_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(templates_module)
                    PromptTemplates = templates_module.PromptTemplates
                else:
                    raise ImportError(f"Cannot find {templates_path}")
                
                self.logger.info("Successfully imported with direct file import")
                
                # Initialize components
                self.model_wrapper = Phi3Wrapper(model_id)
                self.retrieval_engine = RetrievalEngine()
                self.prompt_templates = PromptTemplates()

                if CitationVerifier is not None:
                    try:
                        self.citation_verifier = CitationVerifier()
                        self.logger.info("CitationVerifier initialized (fallback)")
                    except Exception as e:
                        self.logger.warning(f"CitationVerifier initialization failed (fallback): {e}")
                        self.citation_verifier = None
                
                self._initialized = True
                self.logger.info("Phi3MiniEngine components created successfully (direct import)")
                
            except Exception as e2:
                self.logger.error(f"Direct import also failed: {e2}")
                import traceback
                self.logger.error(traceback.format_exc())
                self._initialized = False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Phi3MiniEngine: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the AI engine and load the model"""
        self.logger.info("Initializing Phi-3 Mini Engine...")
        
        try:
            if self.model_wrapper is None:
                self.logger.error("Model wrapper not available - trying to recreate...")
                
                try:
                    from engines.phi3_wrapper import Phi3Wrapper
                except ImportError:
                    try:
                        from llm.engines.phi3_wrapper import Phi3Wrapper
                    except ImportError:
                        self.logger.error("Cannot import Phi3Wrapper")
                        return False
                
                self.model_wrapper = Phi3Wrapper()
                
            if hasattr(self.model_wrapper, 'load_model'):
                success = self.model_wrapper.load_model()
                if success:
                    self.logger.info("Phi-3 Mini Engine initialized successfully")
                    self._initialized = True
                    return True
                else:
                    self.logger.error("Failed to load model")
                    return False
            else:
                self.logger.error("Model wrapper doesn't have load_model method")
                return False
                
        except Exception as e:
            self.logger.error(f"Engine initialization failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def generate_explanation(self, patient_data: Dict, risk_results: Dict, 
                            explanation_type: str = "general", 
                            include_citations: bool = True) -> Dict[str, Any]:
        """Generate AI explanation with RAG support"""
        
        # Check if components are available
        if self.model_wrapper is None:
            self.logger.error("Model wrapper is None")
            # Try to reinitialize
            self.__init__()
            if self.model_wrapper is None:
                return {
                    'success': False,
                    'error': 'Model wrapper could not be initialized'
                }
        
        if self.retrieval_engine is None or self.prompt_templates is None:
            self.logger.error("Required components not available")
            return {
                'success': False,
                'error': 'Required components not available'
            }
        
        try:
            # Ensure model is loaded
            if not hasattr(self.model_wrapper, 'is_loaded'):
                self.logger.error("Model wrapper doesn't have is_loaded attribute")
                return {
                    'success': False,
                    'error': 'Model wrapper not properly initialized'
                }
                
            if not self.model_wrapper.is_loaded:
                self.logger.info("Model not loaded, initializing...")
                if not self.model_wrapper.load_model():
                    return {
                        'success': False,
                        'error': 'Failed to load AI model'
                    }
            
            # Build search query
            query_parts = []
            
            # Add explanation type
            if explanation_type == "diabetes":
                query_parts.append("diabetes risk prevention FINDRISC")
            elif explanation_type == "cardiovascular":
                query_parts.append("cardiovascular disease prevention Framingham")
            elif explanation_type == "colorectal":
                query_parts.append("colorectal cancer screening guidelines")
            else:
                query_parts.append("preventive health screening guidelines")
            
            query = " ".join(query_parts)
            
            # Try full context retrieval if we have all data
            if patient_data and risk_results:
                context_result = self.retrieval_engine.retrieve_context(
                    patient_data=patient_data,
                    risk_results=risk_results,
                    explanation_type=explanation_type,
                    limit=5
                )
            else:
                # Fallback to simple query retrieval
                context_result = self.retrieval_engine.retrieve_context_simple(
                    query=query,
                    limit=5
                )
            
            # Check result format
            if not isinstance(context_result, dict):
                self.logger.warning(f"Invalid retrieval result type: {type(context_result)}")
                context_result = {
                    'success': False,
                    'error': 'Invalid retrieval result format',
                    'sources': [],
                    'context': ''
                }
            
            # Extract context and sources
            if context_result.get('success', False):
                context = context_result.get('context', '')
                sources = context_result.get('sources', [])
            else:
                self.logger.warning(f"Context retrieval failed: {context_result.get('error', 'Unknown error')}")
                # Continue without context
                context = "Based on medical guidelines and evidence-based practices."
                sources = []
            
            # Build prompt with context
            prompt = self.prompt_templates.build_explanation_prompt(
                patient_data=patient_data,
                risk_results=risk_results,
                context={'sources': sources, 'context': context},
                explanation_type=explanation_type
            )
            
            # Generate explanation
            explanation = self.model_wrapper.generate(prompt, max_new_tokens=500)
            
            verification_result = None
            verification_score = 1.0
            flagged_sentences = []
            
            if include_citations and self.citation_verifier and sources:
                self.logger.info("Running citation verification...")
                try:
                    verification_result = self.citation_verifier.verify_explanation(
                        explanation=explanation,
                        sources=sources,
                        strict_mode=strict_verification
                    )
                    
                    if verification_result.get('success', False):
                        original_explanation = explanation
                        explanation = verification_result.get('cleaned_explanation', explanation)
                        verification_score = verification_result.get('verification_score', 0.0)
                        flagged_sentences = verification_result.get('flagged_sentences', [])
                        
                        self.logger.info(f"Verification completed: score={verification_score:.2f}, "
                                    f"flagged={len(flagged_sentences)} sentences")
                        
                        if explanation != original_explanation:
                            self.logger.info("Explanation was modified during verification")
                            
                    else:
                        self.logger.warning(f"Verification failed: {verification_result.get('error', 'Unknown')}")
                        verification_score = 0.0
                        
                except Exception as e:
                    self.logger.error(f"Citation verification error: {e}")
                    verification_score = 0.0
                    flagged_sentences = []
                    
            else:
                # Log why verification was skipped
                if not sources:
                    verification_score = 0.0
                    self.logger.info("No verification: no sources available")
                elif not self.citation_verifier:
                    verification_score = 0.0
                    self.logger.info("No verification: verifier not available")
                elif not include_citations:
                    verification_score = 1.0
                    self.logger.info("No verification: citations disabled")
            
            return {
                'success': True,
                'explanation': explanation,
                'citations': sources,
                'confidence': 0.85,
                'context_sources': len(sources),
                'verification_score': verification_score,     
                'flagged_sentences': flagged_sentences,       
                'verification_details': verification_result   
            }
            
        except Exception as e:
            self.logger.error(f" Explanation generation failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_quick_summary(self, risk_results: Dict[str, Any]) -> str:
        """Generate a quick summary of risk results"""
        try:
            # Check if model wrapper exists
            if self.model_wrapper is None:
                self.logger.error("Model wrapper not initialized - attempting to create")
                # Try one more time to initialize
                self.__init__()
                if self.model_wrapper is None:
                    return "AI model not available - unable to generate summary"
            
            # Check if model is loaded
            if hasattr(self.model_wrapper, 'is_loaded') and not self.model_wrapper.is_loaded:
                self.logger.info("Model not loaded, attempting to initialize...")
                if not self.initialize():
                    # Return a basic summary without AI
                    return self._generate_basic_summary(risk_results)
            
            # Build a simple summary prompt
            summary_parts = []
            
            # Handle different risk_results structures
            if isinstance(risk_results, dict):
                if 'results' in risk_results:
                    calc_results = risk_results.get('results', {})
                else:
                    calc_results = risk_results
            else:
                calc_results = {}
            
            # Extract key findings from the actual result objects
            for calc_name, result in calc_results.items():
                # Skip error results
                if isinstance(result, dict) and 'error' in result:
                    continue
                
                # Handle actual result objects (not dicts)
                try:
                    if calc_name == 'diabetes' and hasattr(result, 'ten_year_risk_percentage'):
                        summary_parts.append(f"Diabetes risk: {result.ten_year_risk_percentage:.1f}%")
                    elif calc_name == 'cardiovascular' and hasattr(result, 'ten_year_risk_percentage'):
                        summary_parts.append(f"CVD risk: {result.ten_year_risk_percentage:.1f}%")
                    elif calc_name == 'colorectal_screening' and hasattr(result, 'recommendation'):
                        rec_value = result.recommendation.value if hasattr(result.recommendation, 'value') else str(result.recommendation)
                        summary_parts.append(f"Colorectal: {rec_value}")
                except Exception as e:
                    self.logger.warning(f"Failed to extract {calc_name} result: {e}")
                    continue
            
            if not summary_parts:
                return "No risk assessment results available for summary."
            
            # If we can't use AI, return basic summary
            if self.model_wrapper is None or not hasattr(self.model_wrapper, 'generate'):
                return self._generate_basic_summary(risk_results)
            
            # Create simple prompt
            prompt = f"""Provide a brief, clear summary of these health risk assessment results:
            
            {', '.join(summary_parts)}
            
            Summary (2-3 sentences):"""
            
            # Generate summary with error handling
            try:
                summary = self.model_wrapper.generate(prompt, max_new_tokens=100, temperature=0.7)
                return summary.strip()
            except Exception as gen_error:
                self.logger.error(f"Generation failed: {gen_error}")
                # Return a basic summary if AI generation fails
                return self._generate_basic_summary(risk_results)
                
        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Return a fallback message
            return self._generate_basic_summary(risk_results)
    
    def _generate_basic_summary(self, risk_results: Dict[str, Any]) -> str:
        """Generate a basic text summary without AI"""
        summary_parts = []
        
        if isinstance(risk_results, dict):
            if 'results' in risk_results:
                calc_results = risk_results.get('results', {})
            else:
                calc_results = risk_results
        else:
            return "Unable to generate summary from results."
        
        for calc_name, result in calc_results.items():
            if isinstance(result, dict) and 'error' in result:
                continue
            
            try:
                if calc_name == 'diabetes' and hasattr(result, 'ten_year_risk_percentage'):
                    risk = result.ten_year_risk_percentage
                    if risk < 7:
                        summary_parts.append(f"Low diabetes risk ({risk:.1f}%)")
                    elif risk < 15:
                        summary_parts.append(f"Moderate diabetes risk ({risk:.1f}%)")
                    else:
                        summary_parts.append(f"High diabetes risk ({risk:.1f}%)")
                        
                elif calc_name == 'cardiovascular' and hasattr(result, 'ten_year_risk_percentage'):
                    risk = result.ten_year_risk_percentage
                    if risk < 7.5:
                        summary_parts.append(f"Low cardiovascular risk ({risk:.1f}%)")
                    elif risk < 20:
                        summary_parts.append(f"Moderate cardiovascular risk ({risk:.1f}%)")
                    else:
                        summary_parts.append(f"High cardiovascular risk ({risk:.1f}%)")
                        
                elif calc_name == 'colorectal_screening' and hasattr(result, 'recommendation'):
                    summary_parts.append("Colorectal screening recommendations available")
            except:
                continue
        
        if summary_parts:
            return f"Assessment Results: {'; '.join(summary_parts)}. Please consult with healthcare providers for personalized recommendations."
        else:
            return "Assessment complete. Please review detailed results above."
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        status = {
            "engine_initialized": self._initialized if hasattr(self, '_initialized') else False,
            "model_wrapper_available": self.model_wrapper is not None,
            "retrieval_engine_available": self.retrieval_engine is not None,
            "prompt_templates_available": self.prompt_templates is not None,
            "citation_verifier_available": self.citation_verifier is not None
        }
        
        if self.model_wrapper is not None:
            status.update({
                "model_loaded": self.model_wrapper.is_loaded if hasattr(self.model_wrapper, 'is_loaded') else False,
                "model_info": self.model_wrapper.get_model_info() if hasattr(self.model_wrapper, 'get_model_info') else {}
            })
        else:
            status.update({
                "model_loaded": False,
                "model_info": {}
            })
        
        if self.retrieval_engine is not None and hasattr(self.retrieval_engine, '_ensure_search_engine'):
            status["retrieval_engine_ready"] = self.retrieval_engine._ensure_search_engine()
        else:
            status["retrieval_engine_ready"] = False
        
        return status
    
    def cleanup(self):
        """Cleanup resources"""
        if self.model_wrapper is not None:
            try:
                self.model_wrapper.unload_model()
            except Exception as e:
                self.logger.error(f"Error during model cleanup: {e}")
        
        self.logger.info("Engine cleanup completed")
    
    def test_citation_verification(self):
        """Test citation verification integration"""
        test_patient = {'age': 45, 'gender': 'male', 'bmi': 28}
        test_results = {'diabetes': type('obj', (object,), {'total_score': 12, 'ten_year_risk_percentage': 15.0})()}
        
        result = self.generate_explanation(
            patient_data=test_patient,
            risk_results={'results': {'diabetes': test_results['diabetes']}},
            explanation_type="diabetes",
            include_citations=True,
            strict_verification=False
        )
        
        print("Citation Verification Test Results:")
        print(f"Success: {result.get('success', False)}")
        print(f"Verification Score: {result.get('verification_score', 0.0):.2f}")
        print(f"Flagged Sentences: {len(result.get('flagged_sentences', []))}")
        print(f"Verifier Available: {self.citation_verifier is not None}")
        
        return result