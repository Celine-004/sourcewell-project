"""
Simple Citation Verification System
Validates AI claims against retrieved evidence
"""
import re
from typing import Dict, Any, List, Tuple
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

class CitationVerifier:
    """Simple citation verification for AI-generated medical explanations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.similarity_model = None
        self.min_similarity_threshold = 0.3
        
    def _ensure_similarity_model(self):
        """Load sentence transformer model for similarity checking"""
        if self.similarity_model is None:
            try:
                self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Similarity model loaded")
            except Exception as e:
                self.logger.error(f"Failed to load similarity model: {e}")
                return False
        return True
    
    def verify_explanation(
        self,
        explanation: str,
        sources: List[Dict[str, Any]],
        strict_mode: bool = False
    ) -> Dict[str, Any]:
        """Verify explanation against source documents"""
        
        try:
            # Split explanation into sentences
            sentences = self._split_into_sentences(explanation)
            
            # Verify each sentence
            verification_results = []
            flagged_sentences = []
            supported_sentences = []
            
            for sentence in sentences:
                if self._is_medical_claim(sentence):
                    verification = self._verify_sentence(sentence, sources, strict_mode)
                    verification_results.append(verification)
                    
                    if verification["supported"]:
                        supported_sentences.append(sentence)
                    else:
                        flagged_sentences.append(sentence)
                else:
                    # Non-medical sentences (disclaimers, general statements) are allowed
                    supported_sentences.append(sentence)
            
            # Calculate overall verification score
            total_medical_claims = len(verification_results)
            supported_claims = sum(1 for v in verification_results if v["supported"])
            
            verification_score = (
                supported_claims / total_medical_claims 
                if total_medical_claims > 0 
                else 1.0
            )
            
            # Generate cleaned explanation if needed
            cleaned_explanation = self._generate_cleaned_explanation(
                explanation, flagged_sentences, strict_mode
            )
            
            return {
                "success": True,
                "verification_score": verification_score,
                "total_claims": total_medical_claims,
                "supported_claims": supported_claims,
                "flagged_sentences": flagged_sentences,
                "cleaned_explanation": cleaned_explanation,
                "original_explanation": explanation,
                "details": verification_results
            }
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "verification_score": 0.0,
                "cleaned_explanation": "Verification failed. Please consult healthcare providers."
            }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_medical_claim(self, sentence: str) -> bool:
        """Determine if sentence makes a medical claim"""
        medical_keywords = [
            'risk', 'factor', 'increase', 'decrease', 'associated', 'cause',
            'prevent', 'treatment', 'therapy', 'medication', 'diet', 'exercise',
            'screening', 'test', 'diagnosis', 'symptom', 'condition', 'disease',
            'study', 'research', 'evidence', 'guideline', 'recommend'
        ]
        
        # Skip obvious disclaimers
        disclaimer_phrases = [
            'consult', 'doctor', 'healthcare', 'medical advice', 'not a substitute',
            'educational only', 'disclaimer'
        ]
        
        sentence_lower = sentence.lower()
        
        # Check for disclaimer phrases first
        if any(phrase in sentence_lower for phrase in disclaimer_phrases):
            return False
        
        # Check for medical content
        return any(keyword in sentence_lower for keyword in medical_keywords)
    
    def _verify_sentence(
        self,
        sentence: str,
        sources: List[Dict[str, Any]],
        strict_mode: bool
    ) -> Dict[str, Any]:
        """Verify a single sentence against sources"""
        
        if not sources:
            return {
                "sentence": sentence,
                "supported": False,
                "confidence": 0.0,
                "supporting_sources": [],
                "reason": "No sources available"
            }
        
        # Collect source texts
        source_texts = []
        for source in sources:
            content = source.get('content', '')
            if content:
                source_texts.append({
                    'text': content,
                    'source': source
                })
        
        if not source_texts:
            return {
                "sentence": sentence,
                "supported": False,
                "confidence": 0.0,
                "supporting_sources": [],
                "reason": "No source content available"
            }
        
        # Simple keyword-based verification
        best_match = self._find_best_keyword_match(sentence, source_texts)
        
        # Use semantic similarity if available
        if self._ensure_similarity_model():
            semantic_match = self._find_best_semantic_match(sentence, source_texts)
            # Combine keyword and semantic scores
            if semantic_match['confidence'] > best_match['confidence']:
                best_match = semantic_match
        
        # Determine if supported based on threshold
        threshold = 0.5 if strict_mode else self.min_similarity_threshold
        supported = best_match['confidence'] >= threshold
        
        return {
            "sentence": sentence,
            "supported": supported,
            "confidence": best_match['confidence'],
            "supporting_sources": [best_match['source']] if supported else [],
            "reason": f"Match confidence: {best_match['confidence']:.2f}"
        }
    
    def _find_best_keyword_match(
        self,
        sentence: str,
        source_texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Find best matching source using keyword overlap"""
        
        sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
        
        best_confidence = 0.0
        best_source = None
        
        for source_data in source_texts:
            source_text = source_data['text'].lower()
            source_words = set(re.findall(r'\b\w+\b', source_text))
            
            # Calculate Jaccard similarity
            intersection = sentence_words & source_words
            union = sentence_words | source_words
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > best_confidence:
                    best_confidence = similarity
                    best_source = source_data['source']
        
        return {
            'confidence': best_confidence,
            'source': best_source
        }
    
    def _find_best_semantic_match(
        self,
        sentence: str,
        source_texts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Find best matching source using semantic similarity"""
        
        try:
            # Encode sentence
            sentence_embedding = self.similarity_model.encode([sentence])
            
            # Encode source texts (limit length to avoid memory issues)
            source_chunks = []
            source_mappings = []
            
            for source_data in source_texts:
                content = source_data['text'][:1000]  # Limit to 1000 chars
                source_chunks.append(content)
                source_mappings.append(source_data['source'])
            
            if not source_chunks:
                return {'confidence': 0.0, 'source': None}
            
            source_embeddings = self.similarity_model.encode(source_chunks)
            
            # Calculate similarities
            similarities = np.inner(sentence_embedding, source_embeddings)[0]
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_confidence = float(similarities[best_idx])
            best_source = source_mappings[best_idx]
            
            return {
                'confidence': best_confidence,
                'source': best_source
            }
            
        except Exception as e:
            self.logger.error(f"Semantic matching failed: {e}")
            return {'confidence': 0.0, 'source': None}
    
    def _generate_cleaned_explanation(
        self,
        original_explanation: str,
        flagged_sentences: List[str],
        strict_mode: bool
    ) -> str:
        """Generate cleaned explanation by handling unsupported claims"""
        
        if not flagged_sentences:
            return original_explanation
        
        cleaned = original_explanation
        
        for flagged_sentence in flagged_sentences:
            if strict_mode:
                # Remove unsupported sentences in strict mode
                cleaned = cleaned.replace(flagged_sentence, "")
            else:
                # Add hedging language in normal mode
                hedged = f"Based on available information, {flagged_sentence.lower()}"
                cleaned = cleaned.replace(flagged_sentence, hedged)
        
        # Clean up extra whitespace and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\s*[.!?]\s*[.!?]\s*', '. ', cleaned)
        
        # Add verification disclaimer
        if flagged_sentences:
            disclaimer = "\n\n*Note: Some claims have limited supporting evidence in our knowledge base. Please consult healthcare providers for complete medical guidance.*"
            cleaned += disclaimer
        
        return cleaned.strip()