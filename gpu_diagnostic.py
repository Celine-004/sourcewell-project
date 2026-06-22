import sys
import os
from pathlib import Path

print("=" * 60)
print("SOURCEWELL GPU DIAGNOSTIC")
print("=" * 60)

# 1. Python version
print(f"\n[1] Python version: {sys.version}")

# 2. PyTorch and CUDA
print("\n[2] PyTorch / CUDA status:")
try:
    import torch
    print(f"    PyTorch version: {torch.__version__}")
    print(f"    CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"    CUDA version: {torch.version.cuda}")
        print(f"    GPU count: {torch.cuda.device_count()}")
        print(f"    GPU name: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        print(f"    GPU memory: {props.total_memory / 1024**3:.1f} GB")
        print(f"    Compute capability: {props.major}.{props.minor}")
        # Quick GPU test
        t = torch.tensor([1.0, 2.0, 3.0]).cuda()
        print(f"    Quick GPU tensor test: {t} — PASSED")
        del t
        torch.cuda.empty_cache()
    else:
        print("    *** CUDA NOT AVAILABLE — this is the root problem ***")
        print(f"    torch.cuda built with: {torch.version.cuda if hasattr(torch.version, 'cuda') else 'NO CUDA'}")
except ImportError:
    print("    *** PyTorch NOT INSTALLED ***")

# 3. bitsandbytes
print("\n[3] bitsandbytes status:")
try:
    import bitsandbytes as bnb
    print(f"    Version: {bnb.__version__}")
    # Try to actually use it
    if torch.cuda.is_available():
        try:
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            print(f"    BitsAndBytesConfig created successfully")
        except Exception as e:
            print(f"    BitsAndBytesConfig FAILED: {e}")
    else:
        print("    Skipping bnb config test (no CUDA)")
except ImportError:
    print("    *** bitsandbytes NOT INSTALLED ***")
except Exception as e:
    print(f"    *** bitsandbytes import error: {e} ***")

# 4. transformers version
print("\n[4] Transformers status:")
try:
    import transformers
    print(f"    Version: {transformers.__version__}")
except ImportError:
    print("    *** transformers NOT INSTALLED ***")

# 5. accelerate version
print("\n[5] Accelerate status:")
try:
    import accelerate
    print(f"    Version: {accelerate.__version__}")
except ImportError:
    print("    *** accelerate NOT INSTALLED ***")

# 6. sourcewell_config.json check
print("\n[6] sourcewell_config.json check:")
config_path = Path("sourcewell_config.json")
if config_path.exists():
    import json
    with open(config_path) as f:
        config = json.load(f)
    cache_paths = config.get("cache_paths", {})
    hf_cache = cache_paths.get("huggingface", "NOT SET")
    print(f"    HF cache path: {hf_cache}")
    print(f"    Path exists: {Path(hf_cache).exists()}")
    model_cache = Path(hf_cache) / "models--microsoft--Phi-3-mini-4k-instruct"
    print(f"    Phi-3 model cache exists: {model_cache.exists()}")
    if model_cache.exists():
        # Check for snapshots
        snapshots = model_cache / "snapshots"
        if snapshots.exists():
            snapshot_dirs = list(snapshots.iterdir())
            print(f"    Snapshot directories: {len(snapshot_dirs)}")
        else:
            print(f"    *** No snapshots directory — model may be incomplete ***")
    versions = config.get("versions", {})
    print(f"    Config pytorch version: {versions.get('pytorch_version', 'NOT SET')}")
    print(f"    Config cuda version: {versions.get('cuda_version', 'NOT SET')}")
    print(f"    Config bnb version: {versions.get('bitsandbytes_version', 'NOT SET')}")
else:
    print("    *** sourcewell_config.json NOT FOUND ***")

# 7. Try actual model load on GPU (the critical test)
print("\n[7] Attempting Phi-3 model load (this is the real test):")
if torch.cuda.is_available():
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        hf_cache = config.get("cache_paths", {}).get("huggingface", ".cache/huggingface")
        model_id = "microsoft/Phi-3-mini-4k-instruct"
        
        print("    Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_id, trust_remote_code=True, cache_dir=hf_cache, local_files_only=True
        )
        print("    Tokenizer loaded OK")
        
        print("    Attempting 4-bit quantized load on GPU...")
        try:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                trust_remote_code=True,
                cache_dir=hf_cache,
                local_files_only=True,
                attn_implementation="eager"
            )
            model_device = next(model.parameters()).device
            print(f"    4-bit model loaded! Device: {model_device}")
            
            # Quick generation test
            print("    Running quick generation test...")
            inputs = tokenizer("Hello", return_tensors="pt").to(model_device)
            outputs = model.generate(**inputs, max_new_tokens=5)
            result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"    Generation test output: '{result[:50]}...'")
            print("    *** 4-BIT GPU INFERENCE WORKS ***")
            
            del model, tokenizer
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"    *** 4-bit load FAILED: {e} ***")
            print("    This is likely why the app falls back to CPU.")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"    *** Model load test FAILED: {e} ***")
        import traceback
        traceback.print_exc()
else:
    print("    Skipping model load (CUDA not available)")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
