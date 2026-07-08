# SourceWell LLM Module

AI-powered medical explanation system using Qwen3-4B with 4-bit quantization, RAG-based evidence retrieval, citation verification, and an AI coaching chat.

## Overview

The LLM module generates personalized medical explanations for patient risk assessments. It runs Qwen3-4B locally on GPU with 4-bit quantization (~2.6GB VRAM), retrieves evidence from the Weaviate knowledge base, verifies AI claims against medical sources, and provides a coaching chat for follow-up health questions.

The module also retains the original Phi-3 Mini engine files for reference, though Qwen3 is the active engine.

## Architecture

```
llm/ 
├── qwen3_engine.py        # Primary engine: orchestration, RAG, prompts, coaching chat 
├── phi3_engine.py         # Archived Phi-3 engine (reference only) 
├── citation_verifier.py   # Verifies AI claims against medical sources 
├── engines/ 
│ ├── qwen3_wrapper.py     # Qwen3-4B model loading, quantization, generation 
│ └── phi3_wrapper.py      # Archived Phi-3 wrapper (reference only) 
├── rag/ 
│ └── retrieval_engine.py  # Knowledge base retrieval via Weaviate 
└── utils/ 
  └── prompt_templates.py  # Condition-specific prompt construction
```

Data Flow: Patient Data → RAG Evidence Retrieval → Prompt Construction (with sources) → Qwen3 Generation → Citation Verification → Output

## Hardware Requirements

The module has been validated on the following configuration:

- **GPU**: NVIDIA GTX 1060 (6GB VRAM) — 2.6GB used by model, ~3.3GB headroom for generation
- **RAM**: 16GB system memory
- **Storage**: ~8GB for Qwen3-4B model cache
- **CUDA**: 12.1 with PyTorch 2.3.1

Other NVIDIA GPUs with 4GB+ VRAM should work. CPU fallback is available but significantly slower. macOS MPS support has not been validated.

## Key Components

### Qwen3Engine (`qwen3_engine.py`)

The primary orchestration class that handles explanation generation, quick summaries, and coaching chat responses.

```python
from llm.qwen3_engine import Qwen3Engine

engine = Qwen3Engine()
engine.initialize()

# Generate a condition-specific explanation
result = engine.generate_explanation(
    patient_data=patient_data,
    risk_results=risk_results,
    explanation_type="diabetes",      # diabetes | cardiovascular | colorectal | general
    include_citations=True,
    verify_claims=True,
    detailed=False                    # True for extended 4-6 paragraph output
)

# Quick summary (2-3 sentences)
summary = engine.generate_quick_summary(risk_results)

# Coaching chat
response = engine.generate_coaching_response(
    user_message="What should I eat to lower my diabetes risk?",
    risk_context=risk_results,
    chat_history=[]
)
```

### Qwen3Wrapper (engines/qwen3_wrapper.py)

Handles model loading with 4-bit quantization (NF4, double quantization via bitsandbytes), attention mechanism selection (SDPA preferred for Pascal GPUs, with eager fallback), VRAM monitoring, and post-generation cleanup including non-ASCII character filtering.

### Prompt Templates (utils/prompt_templates.py)

Constructs condition-specific prompts with dynamic source configuration. Each explanation type (diabetes, cardiovascular, colorectal, general) has a tailored prompt that restricts the model to discussing only the relevant condition, references the appropriate clinical guidelines (ADA, ACC/AHA, USPSTF), and configures source count and character limits independently.

### Citation Verifier (citation_verifier.py)

Compares AI-generated claims against retrieved medical sources to produce a verification score. Flags unsupported sentences and provides verification details alongside the explanation.

### RAG Retrieval (rag/retrieval_engine.py)

Queries the Weaviate knowledge base for condition-relevant medical evidence, which is injected into the prompt as numbered sources for the model to reference.

### Explanation Output Structure

```python
{
    'success': True,
    'explanation': "Based on your FINDRISC score of 15...",
    'citations': [
        {'title': '...', 'citation': '...', 'content_preview': '...'}
    ],
    'confidence': 1.0,              # Evidence coverage: min(sources_found, target) / target
    'verification_score': 0.82,     # Claim-to-source match accuracy
    'flagged_sentences': [],        # Sentences without source support
    'verification_details': {...},  # Full verification breakdown
    'sources_used': 3,
    'sources_available': 5
}
```

### Configuration

The model ID is configured in setup_sourcewell.py as DEFAULT_AI_MODEL_ID = "Qwen/Qwen3-4B". Generation parameters (max tokens, temperature, repetition penalty) are set in qwen3_engine.py and qwen3_wrapper.py. Prompt source limits are configured per explanation type in prompt_templates.py.

### Troubleshooting

If the model fails to load, verify CUDA availability with python -c "import torch; print(torch.cuda.is_available())" and check that bitsandbytes is installed (pip show bitsandbytes). If generation produces unexpected characters or stale behavior persists after code changes, clear the Python bytecode cache:

```bash
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

If VRAM runs out during generation, the wrapper automatically clears the CUDA cache when usage exceeds 95%. For persistent OOM errors, reduce max_new_tokens in the engine configuration. For comprehensive GPU diagnostics, run python gpu_diagnostic.py from the project root.
