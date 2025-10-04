# SourceWell LLM Module

A robust medical AI explanation system with comprehensive error handling and fallback mechanisms for healthcare applications.

## Overview

The SourceWell LLM Module provides AI-powered medical explanation generation using Microsoft's Phi-3 Mini model. The system is designed with extensive error handling, graceful degradation, and fallback mechanisms to ensure reliable operation in healthcare environments where system availability is critical.

**Key Design Principles:**

- Graceful failure handling with text-based fallbacks
- Extensive error logging and status monitoring
- Multiple component initialization strategies
- Resource cleanup and memory management
- Medical compliance safeguards

## Architecture

```
SourceWell LLM Module
├── __init__.py                    # Module API and component exports
├── phi3_engine.py                 # Core orchestration engine with error handling
├── citation_verifier.py           # AI claim verification against medical sources
├── engines/
│   ├── __init__.py
│   └── phi3_wrapper.py           # Phi-3 Mini model wrapper
├── rag/
│   ├── __init__.py
│   └── retrieval_engine.py       # Knowledge base retrieval
└── utils/
    ├── __init__.py
    └── prompt_templates.py       # Medical prompt templates

Data Flow:
Patient Data → Component Validation → RAG Retrieval → AI Generation → Citation Verification → Fallback if Failed
```

## Installation

### System Requirements

- **Python 3.8+**
- **RAM**: 8GB minimum (16GB recommended for GPU)
- **GPU**: NVIDIA GPU with 4GB+ VRAM (optional, CPU fallback available)
- **Storage**: 5GB for models and cache

### Dependencies

**Automated Setup (Recommended):**

```bash
# NOTE: Automated setup script availability should be verified
# python setup_sourcewell.py          # Interactive setup with hardware detection
# python setup_sourcewell.py --auto   # Automatic installation
```

**Manual Installation:**

```bash
pip install torch transformers sentence-transformers
pip install bitsandbytes  # GPU quantization (optional)
pip install weaviate-client PyYAML logging
```

**Platform-Specific Installation Notes:**

*Windows:*

- Ensure Microsoft Visual C++ Build Tools are installed
- For NVIDIA GPUs, install CUDA Toolkit 11.8+ before running setup
- Use Command Prompt(not Git Bash) for setup commands

*macOS:*

- Xcode Command Line Tools required: `xcode-select --install`
- Apple Silicon Macs use Metal Performance Shaders (MPS) for acceleration
- Intel Macs can use CPU mode or external GPU solutions

*Linux:*

- GCC/G++ compiler required for some dependencies
- For NVIDIA GPUs, ensure CUDA drivers and toolkit are installed
- AMD GPUs require ROCm installation for acceleration

## Core Engine API

### Phi3MiniEngine

The main orchestration class with comprehensive error handling:

```python
from llm.phi3_engine import Phi3MiniEngine

# Initialize with automatic fallback handling
engine = Phi3MiniEngine(model_id="microsoft/Phi-3-mini-4k-instruct")

# Check initialization status
if engine._initialized:
    print("Engine components loaded successfully")
else:
    print("Engine running in fallback mode")
```

**Actual Generation Parameters:**

```python
default_generation_params = {
    "max_new_tokens": 1024,        # As implemented in code
    "temperature": 0.7,            # Balanced for medical content
    "top_p": 0.9,                 # Nucleus sampling
    "repetition_penalty": 1.1      # Reduce repetition
}
```

### Key Methods

#### generate_explanation()

Generates medical explanations with comprehensive error handling:

```python
result = engine.generate_explanation(
    patient_data={
        "age": 52,
        "bmi": 28.5,
        "family_diabetes_history": "parent"
    },
    risk_results={
        "diabetes": {"ten_year_risk_percentage": 15.2}
    },
    explanation_type="diabetes",
    include_citations=True,  # Enables citation verification
strict_verification=False  # Optional: Enable strict verification mode
)

# Check result structure
if result['success']:
    print(f"Explanation: {result['explanation']}")
    print(f"Citations: {len(result['citations'])} sources")
    print(f"Confidence: {result['confidence']}")
    print(f"Verification Score: {result['verification_score']}")
    print(f"Flagged Sentences: {len(result['flagged_sentences'])}")
else:
    print(f"Generation failed: {result['error']}")
    # System continues with fallback content
```

#### generate_quick_summary()

Provides summaries with automatic AI/text fallbacks:

```python
# Will attempt AI generation, fall back to basic text if needed
summary = engine.generate_quick_summary(risk_results)

# Examples of actual fallback responses:
# "AI model not available - unable to generate summary"
# "Assessment Results: Low diabetes risk (4.2%); Moderate cardiovascular risk (12.1%)"
```

#### get_engine_status()

Monitor system health and component availability:

```python
status = engine.get_engine_status()
print(f"Engine initialized: {status['engine_initialized']}")
print(f"Model loaded: {status['model_loaded']}")
print(f"RAG available: {status['retrieval_engine_available']}")
print(f"Templates ready: {status['prompt_templates_available']}")
print(f"Citation verifier: {status['citation_verifier_available']}")
print(f"RAG ready: {status['retrieval_engine_ready']}")
```

## Error Handling and Reliability

### Component Initialization

The engine attempts multiple strategies to load components:

```python
# 1. Standard imports
try:
    from llm.engines.phi3_wrapper import Phi3Wrapper
except ImportError:
    # 2. Direct file imports
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(...)
        # Load components directly from files
    except Exception:
        # 3. Graceful degradation
        self._initialized = False
        # System continues with limited functionality
```

### Graceful Degradation

**Citation Verifier Initialization:**

The engine attempts to load the citation verifier with multiple fallback strategies:

```python
# 1. Standard import from llm.utils
try:
    from llm.utils.citation_verifier import CitationVerifier
except ImportError:
    # 2. Relative import  
    try:
        from .utils.citation_verifier import CitationVerifier
    except ImportError:
        # 3. Direct import
        try:
            from utils.citation_verifier import CitationVerifier
        except ImportError:
            # 4. Graceful degradation
            CitationVerifier = None
            logger.warning("CitationVerifier not available")
```

When AI components fail, the system provides meaningful fallbacks:

```python
def _generate_basic_summary(self, risk_results: Dict[str, Any]) -> str:
    """Generate text summary without AI when models unavailable"""
    # Actual implementation from code:
    if risk < 7:
        summary_parts.append(f"Low diabetes risk ({risk:.1f}%)")
    elif risk < 15:
        summary_parts.append(f"Moderate diabetes risk ({risk:.1f}%)")
    else:
        summary_parts.append(f"High diabetes risk ({risk:.1f}%)")
  
    return f"Assessment Results: {'; '.join(summary_parts)}. Please consult with healthcare providers."
```

### Error Response Patterns

All methods return structured error responses:

```python
# Consistent error response format
{
    'success': False,
    'error': 'Model wrapper could not be initialized',
    'explanation': None,
    'citations': [],  # Sources from RAG retrieval
    'verification_score': 0.0,  # Citation verification confidence (0.0-1.0)
    'flagged_sentences': [],  # Sentences flagged during verification
    'verification_details': None,  # Full verification result object
    'confidence': 0.85  # Fixed confidence score for successful generation
}
```

## Performance Expectations

### Model Loading

- **First run**: 5-15 minutes (model download ~2.4GB for Phi-3-mini-4k-instruct)
- **Subsequent runs**: 15-60 seconds (model loading)
- **Generation**: 5-180 seconds per explanation (varies by length and hardware)

*Note: These times are estimates and may vary significantly based on your specific hardware configuration, network speed, system load, and available memory.*

### Memory Usage

- **CPU mode**: ~2-4GB RAM for model
- **GPU with quantization**: ~1-2GB VRAM + 2GB RAM
- **GPU without quantization**: ~2-4GB VRAM + 2GB RAM

*Note: Memory usage may vary based on model configuration, batch size, and system optimization settings.*

### Hardware Performance

**Reference Performance (Approximate):**

- **High-end GPU**: ~2-15 seconds per generation (performance varies)
- **Mid-range GPU**: ~5-300 seconds per generation (performance varies)
- **Apple Silicon**: ~8-45 seconds per generation (MPS support requires verification)
- **CPU only**: ~30-600 seconds per generation (highly variable)
- **Older hardware**: May require 2-10 minutes per generation

**Important Performance Disclaimers:**

**Actual performance will vary significantly based on:**

- Specific GPU model and VRAM capacity
- CPU specifications and core count
- Available system RAM and storage speed
- Background processes and system load
- Power management settings
- Driver versions and optimization
- Thermal throttling under sustained load

**IMPORTANT: These benchmarks are rough estimates based on typical hardware performance patterns. Actual performance may vary significantly and has not been comprehensively tested across all listed hardware configurations. Do not rely on these estimates for system planning without conducting your own performance testing.**

**Platform-Specific GPU Support:**

- **Windows/Linux**: NVIDIA CUDA (verified), AMD ROCm (requires verification)
- **macOS**: Apple Metal Performance Shaders (MPS support requires verification)
- **All platforms**: CPU fallback available

## Integration Example

```python
import logging
from llm.phi3_engine import Phi3MiniEngine

# Enable detailed logging to monitor system behavior
logging.basicConfig(level=logging.INFO)

# Initialize engine (may take time on first run)
engine = Phi3MiniEngine()

# Always check status before use
status = engine.get_engine_status()
if not status['engine_initialized']:
    print("Warning: Engine not fully initialized - using fallback mode")

# Generate explanation with error handling
try:
    result = engine.generate_explanation(
        patient_data=patient_data,
        risk_results=risk_results,
        explanation_type="diabetes"
    )
  
    if result['success']:
        # Use AI-generated explanation
        explanation = result['explanation']
    else:
        # Handle failure gracefully
        explanation = "Please consult with your healthcare provider for personalized risk assessment."
  
except Exception as e:
    # Final fallback for unexpected errors
    logger.error(f"Explanation generation failed: {e}")
    explanation = "Risk assessment completed. Please review results with your healthcare provider."

# Cleanup resources when done
finally:
    engine.cleanup()
```

## Troubleshooting

### Common Issues and Solutions

**1. Component Import Failures**

*Linux/macOS:*

```bash
# Check log for specific import errors
tail -f logs/phi3_engine.log

# Verify required files exist
ls -la llm/engines/phi3_wrapper.py
ls -la llm/rag/retrieval_engine.py
ls -la llm/utils/prompt_templates.py
```

*Windows:*

```cmd
# Check log for specific import errors
Get-Content logs/phi3_engine.log -Wait -Tail 10

# Verify required files exist
dir llm\engines\phi3_wrapper.py
dir llm\rag\retrieval_engine.py
dir llm\utils\prompt_templates.py
```

**2. Model Loading Issues**

```python
# Check model status
status = engine.get_engine_status()
if not status['model_loaded']:
    # Try manual initialization
    success = engine.initialize()
    if not success:
        # System will use text fallbacks
        print("Operating in text-only mode")
```

**3. Memory Issues**

```python
# Monitor GPU memory
import torch
if torch.cuda.is_available():
    print(f"GPU Memory: {torch.cuda.memory_allocated() / 1e9:.1f}GB")

# Clear cache if needed
torch.cuda.empty_cache()

# Restart engine if necessary
engine.cleanup()
engine = Phi3MiniEngine()
```

**4. Knowledge Base Connection**

```python
# Check RAG system status
status = engine.get_engine_status()
if not status['retrieval_engine_ready']:
    # System will generate explanations without external context
    print("Warning: Knowledge base unavailable - using model knowledge only")
```

## Limitations and Considerations

### Current Limitations

1. **Model Dependencies**: Requires internet connection for initial model download
2. **Hardware Requirements**: GPU recommended but not required (CPU fallback available)
3. **Knowledge Base**: RAG features require external search backend (implementation details require verification)
4. **Language Support**: English medical content only
5. **Generation Speed**: Varies significantly by hardware (5-120 seconds)

### Medical Safety Considerations

- **AI Generated Content**: All explanations are AI-generated and require clinical validation
- **Fallback Content**: When AI fails, basic text summaries are provided
- **Source Attribution**: Citations provided when available, but not guaranteed
- **Professional Oversight**: All content should be reviewed by qualified healthcare professionals

### Production Deployment Notes

```python
# Recommended production configuration
engine = Phi3MiniEngine()

# Monitor system health
def health_check():
    status = engine.get_engine_status()
    return {
        'healthy': status['engine_initialized'],
        'ai_available': status['model_loaded'],
        'rag_available': status['retrieval_engine_ready']
    }

# Implement timeouts for generation
import signal
def timeout_handler(signum, frame):
    raise TimeoutError("Generation timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout
try:
    result = engine.generate_explanation(...)
finally:
    signal.alarm(0)  # Cancel timeout
```

## Support and Maintenance

### Status Monitoring

```python
# Regular health checks
status = engine.get_engine_status()
metrics = {
    'component_health': all([
        status['engine_initialized'],
        status['model_wrapper_available'],
        status['prompt_templates_available']
    ]),
    'ai_capability': status['model_loaded'],
    'rag_capability': status['retrieval_engine_ready']
}
```

### Resource Cleanup

```python
# Proper shutdown sequence
def shutdown_engine():
    try:
        engine.cleanup()  # Unloads model and clears GPU memory
        logger.info("Engine cleanup completed successfully")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        # Force cleanup if needed
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
```

**Platform-Specific Process Management:**

*Linux/macOS:*

```bash
# Monitor GPU memory usage
nvidia-smi  # For NVIDIA GPUs
watch -n 1 nvidia-smi  # Continuous monitoring

# Kill process if needed
pkill -f "python.*phi3_engine"
```

*Windows:*

```cmd
# Monitor GPU memory usage
nvidia-smi  # For NVIDIA GPUs

# Kill process if needed
taskkill /f /im python.exe
# Or more specific:
wmic process where "commandline like '%phi3_engine%'" delete
```

## Medical Compliance

**Important Disclaimers:**

- This system generates educational content based on risk assessment data
- All AI-generated explanations require clinical validation
- System includes fallback mechanisms but cannot guarantee 100% uptime

**Regulatory Considerations:**

- Implement additional validation for clinical use
- Establish audit trails for AI-generated content
- Ensure compliance with local healthcare regulations
- Maintain human oversight of all AI outputs

## Version Compatibility

- **Phi-3 Mini**: microsoft/Phi-3-mini-4k-instruct
- **PyTorch**: 2.0+ (with CUDA 11.8+ for GPU acceleration)
- **Python**: 3.8+ (3.10+ recommended)
- **Weaviate**: 1.20+ for knowledge base features

This documentation reflects the actual implementation capabilities and limitations of the LLM Module as implemented in the codebase.
