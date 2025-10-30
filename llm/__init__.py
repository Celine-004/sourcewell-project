"""LLM module for SourceWell Healthcare Platform"""

from pathlib import Path
import sys

llm_dir = Path(__file__).parent
sys.path.insert(0, str(llm_dir))

try:
    from .phi3_engine import Phi3MiniEngine
    from .citation_verifier import CitationVerifier
    __all__ = ['Phi3MiniEngine', 'CitationVerifier']
except ImportError:
    __all__ = []