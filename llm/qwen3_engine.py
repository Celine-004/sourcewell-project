"""
Qwen3 Local AI Engine
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

# Citation verifier import
try:
    from llm.citation_verifier import CitationVerifier
except ImportError:
    try:
        from citation_verifier import CitationVerifier
    except ImportError:
        logger.warning("CitationVerifier not available - verification will be disabled")
        CitationVerifier = None


class Qwen3Engine:
    """Local Qwen3 inference engine with RAG capabilities"""

    def __init__(self, model_id: str = "Qwen/Qwen3-4B"):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize all attributes
        self.model_wrapper = None
        self.retrieval_engine = None
        self.prompt_templates = None
        self.citation_verifier = None
        self._initialized = False

        self.default_generation_params = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.15
        }

        try:
            self.logger.info("Importing Qwen3 engine components...")

            from llm.engines.qwen3_wrapper import Qwen3Wrapper
            from llm.rag.retrieval_engine import RetrievalEngine
            from llm.utils.prompt_templates import PromptTemplates

            self.model_wrapper = Qwen3Wrapper(model_id)
            self.retrieval_engine = RetrievalEngine()
            self.prompt_templates = PromptTemplates()

            if CitationVerifier is not None:
                try:
                    self.citation_verifier = CitationVerifier()
                    self.logger.info("CitationVerifier initialized")
                except Exception as e:
                    self.logger.warning(f"CitationVerifier init failed: {e}")
                    self.citation_verifier = None

            self._initialized = True
            self.logger.info("Qwen3Engine initialized successfully")

        except ImportError as e:
            self.logger.error(f"Import failed: {e}")
            self._try_direct_imports(model_id)

        except Exception as e:
            self.logger.error(f"Failed to initialize Qwen3Engine: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self._initialized = False

    def _try_direct_imports(self, model_id: str):
        """Fallback: import components directly from file paths"""
        try:
            import importlib.util

            components = {
                'wrapper': ('qwen3_wrapper', Path(__file__).parent / 'engines' / 'qwen3_wrapper.py', 'Qwen3Wrapper'),
                'retrieval': ('retrieval_engine', Path(__file__).parent / 'rag' / 'retrieval_engine.py', 'RetrievalEngine'),
                'templates': ('prompt_templates', Path(__file__).parent / 'utils' / 'prompt_templates.py', 'PromptTemplates'),
            }

            loaded = {}
            for key, (module_name, path, class_name) in components.items():
                if not path.exists():
                    raise ImportError(f"Cannot find {path}")
                spec = importlib.util.spec_from_file_location(module_name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                loaded[key] = getattr(module, class_name)

            self.model_wrapper = loaded['wrapper'](model_id)
            self.retrieval_engine = loaded['retrieval']()
            self.prompt_templates = loaded['templates']()

            if CitationVerifier is not None:
                try:
                    self.citation_verifier = CitationVerifier()
                    self.logger.info("CitationVerifier initialized (fallback)")
                except Exception as e:
                    self.logger.warning(f"CitationVerifier init failed (fallback): {e}")

            self._initialized = True
            self.logger.info("Qwen3Engine initialized via direct import")

        except Exception as e:
            self.logger.error(f"Direct import failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self._initialized = False

    def initialize(self) -> bool:
        """Load the model into memory"""
        self.logger.info("Initializing Qwen3 Engine...")

        try:
            if self.model_wrapper is None:
                self.logger.error("Model wrapper not available")
                return False

            success = self.model_wrapper.load_model()
            if success:
                self.logger.info("Qwen3 Engine initialized successfully")
                self._initialized = True
                return True
            else:
                self.logger.error("Failed to load model")
                return False

        except Exception as e:
            self.logger.error(f"Engine initialization failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def generate_explanation(self, patient_data: Dict, risk_results: Dict,
                            explanation_type: str = "general",
                            include_citations: bool = True,
                            strict_verification: bool = False,
                            detailed: bool = False) -> Dict[str, Any]:
        """Generate AI explanation with RAG support"""

        if self.model_wrapper is None:
            return {'success': False, 'error': 'Model wrapper not initialized'}

        if self.retrieval_engine is None or self.prompt_templates is None:
            return {'success': False, 'error': 'Required components not available'}

        try:
            # Ensure model is loaded
            if not self.model_wrapper.is_loaded:
                self.logger.info("Model not loaded, loading...")
                if not self.model_wrapper.load_model():
                    return {'success': False, 'error': 'Failed to load AI model'}

            # Retrieve evidence from knowledge base
            if patient_data and risk_results:
                context_result = self.retrieval_engine.retrieve_context(
                    patient_data=patient_data,
                    risk_results=risk_results,
                    explanation_type=explanation_type,
                    limit=5
                )
            else:
                query = self._build_search_query(explanation_type)
                context_result = self.retrieval_engine.retrieve_context_simple(
                    query=query, limit=5
                )

            # Normalize retrieval result
            if not isinstance(context_result, dict):
                context_result = {'success': False, 'sources': [], 'context': ''}

            if context_result.get('success', False):
                context = context_result.get('context', '')
                sources = context_result.get('sources', [])
            else:
                self.logger.warning(f"Retrieval failed: {context_result.get('error', 'Unknown')}")
                context = "Based on medical guidelines and evidence-based practices."
                sources = []

            # Build separated prompts
            system_prompt = self.prompt_templates.build_system_prompt()
            report_prompt = self.prompt_templates.build_report_prompt(
                patient_data=patient_data,
                risk_results=risk_results,
                context={'sources': sources, 'context': context},
                explanation_type=explanation_type,
                detailed=detailed
            )

            # Generate with chat template
            max_tokens = 768 if detailed else 512
            explanation = self.model_wrapper.generate_with_system_prompt(
                system_prompt=system_prompt,
                user_prompt=report_prompt,
                max_new_tokens=max_tokens
            )

            # Citation verification
            verification_score = 0.0
            flagged_sentences = []
            verification_result = None

            if include_citations and self.citation_verifier and sources:
                self.logger.info("Running citation verification...")
                try:
                    verification_result = self.citation_verifier.verify_explanation(
                        explanation=explanation,
                        sources=sources,
                        strict_mode=strict_verification
                    )

                    if verification_result.get('success', False):
                        original = explanation
                        explanation = verification_result.get('cleaned_explanation', explanation)
                        verification_score = verification_result.get('verification_score', 0.0)
                        flagged_sentences = verification_result.get('flagged_sentences', [])

                        self.logger.info(
                            f"Verification: score={verification_score:.2f}, "
                            f"flagged={len(flagged_sentences)}"
                        )

                        if explanation != original:
                            self.logger.info("Explanation modified during verification")
                    else:
                        self.logger.warning(f"Verification failed: {verification_result.get('error')}")

                except Exception as e:
                    self.logger.error(f"Citation verification error: {e}")

            elif not sources:
                self.logger.info("No verification: no sources available")
            elif not self.citation_verifier:
                self.logger.info("No verification: verifier not available")
            elif not include_citations:
                verification_score = 1.0
                self.logger.info("No verification: citations disabled")

            # Limit sources to what the model actually used
            source_config = self.prompt_templates._get_source_config(explanation_type)
            used_sources = sources[:source_config['count']]

            return {
                'success': True,
                'explanation': explanation,
                'citations': used_sources,
                'confidence': min(len(sources), source_config['count']) / source_config['count'],
                'context_sources': len(used_sources),
                'verification_score': verification_score,
                'flagged_sentences': flagged_sentences,
                'verification_details': verification_result
            }

        except Exception as e:
            self.logger.error(f"Explanation generation failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}

    def generate_quick_summary(self, risk_results: Dict[str, Any]) -> str:
        """Generate a quick summary of risk results"""
        try:
            if self.model_wrapper is None:
                return self._generate_basic_summary(risk_results)

            if not self.model_wrapper.is_loaded:
                if not self.initialize():
                    return self._generate_basic_summary(risk_results)

            summary_parts = self._extract_result_parts(risk_results)

            if not summary_parts:
                return "No risk assessment results available for summary."

            system_prompt = "You are a preventive health advisor. Provide brief, clear summaries."
            user_prompt = (
                f"Summarize these health risk results in 2-3 sentences:\n\n"
                f"{', '.join(summary_parts)}"
            )

            summary = self.model_wrapper.generate_with_system_prompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_new_tokens=100,
                temperature=0.7
            )

            return summary.strip()

        except Exception as e:
            self.logger.error(f"Summary generation failed: {e}")
            return self._generate_basic_summary(risk_results)

    def _build_search_query(self, explanation_type: str) -> str:
        """Build search query based on explanation type"""
        queries = {
            "diabetes": "diabetes risk prevention FINDRISC",
            "cardiovascular": "cardiovascular disease prevention Framingham",
            "colorectal": "colorectal cancer screening guidelines",
        }
        return queries.get(explanation_type, "preventive health screening guidelines")

    def _extract_result_parts(self, risk_results: Dict) -> List[str]:
        """Extract readable result strings from risk results"""
        parts = []

        if isinstance(risk_results, dict):
            calc_results = risk_results.get('results', risk_results)
        else:
            return parts

        for calc_name, result in calc_results.items():
            if isinstance(result, dict) and 'error' in result:
                continue

            try:
                if calc_name == 'diabetes' and hasattr(result, 'ten_year_risk_percentage'):
                    parts.append(f"Diabetes risk: {result.ten_year_risk_percentage:.1f}%")
                elif calc_name == 'cardiovascular' and hasattr(result, 'ten_year_risk_percentage'):
                    parts.append(f"CVD risk: {result.ten_year_risk_percentage:.1f}%")
                elif calc_name == 'colorectal_screening' and hasattr(result, 'recommendation'):
                    rec = result.recommendation.value if hasattr(result.recommendation, 'value') else str(result.recommendation)
                    parts.append(f"Colorectal: {rec}")
            except Exception as e:
                self.logger.warning(f"Failed to extract {calc_name}: {e}")

        return parts

    def _generate_basic_summary(self, risk_results: Dict[str, Any]) -> str:
        """Generate a basic text summary without AI"""
        parts = self._extract_result_parts(risk_results)

        if parts:
            return (
                f"Assessment Results: {'; '.join(parts)}. "
                f"Please consult with healthcare providers for personalized recommendations."
            )
        return "Assessment complete. Please review detailed results above."

    def get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        status = {
            "engine": "Qwen3Engine",
            "engine_initialized": self._initialized,
            "model_wrapper_available": self.model_wrapper is not None,
            "retrieval_engine_available": self.retrieval_engine is not None,
            "prompt_templates_available": self.prompt_templates is not None,
            "citation_verifier_available": self.citation_verifier is not None
        }

        if self.model_wrapper is not None:
            status["model_loaded"] = getattr(self.model_wrapper, 'is_loaded', False)
            status["model_info"] = self.model_wrapper.get_model_info() if hasattr(self.model_wrapper, 'get_model_info') else {}
        else:
            status["model_loaded"] = False
            status["model_info"] = {}

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
                self.logger.error(f"Error during cleanup: {e}")
        self.logger.info("Qwen3Engine cleanup completed")
