"""
Phi-3 Mini Model Wrapper - Optimized with 4-bit quantization
"""
import os
import json
import torch
import gc
import time
import random
import numpy as np
import logging
import platform
from pathlib import Path 
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from typing import Dict, Any, Optional, List
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", message=".*torch_dtype.*deprecated.*")
warnings.filterwarnings("ignore", message=".*flash-attention.*")
warnings.filterwarnings("ignore", message=".*TRANSFORMERS_CACHE.*")

class Phi3Wrapper:
    """Wrapper for Phi-3 Mini model optimized for maximum GPU utilization with 4-bit quantization"""
    
    def __init__(self, model_id: str = None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Detect platform for cross-platform support
        self.platform = platform.system().lower()
        self.is_windows = self.platform == 'windows'
        self.is_linux = self.platform == 'linux'
        self.is_mac = self.platform == 'darwin'
        
        project_root = Path(__file__).resolve().parents[2]
        config_file = project_root / "sourcewell_config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Set environment variables from config
            cache_paths = config.get('cache_paths', {})
            os.environ.pop('TRANSFORMERS_CACHE', None)
            os.environ['HF_HOME'] = cache_paths.get('huggingface', str(project_root / '.cache' / 'huggingface'))
            os.environ['TEMP'] = cache_paths.get('temp', str(project_root / '.cache' / 'temp'))
            os.environ['TMP'] = cache_paths.get('temp', str(project_root / '.cache' / 'temp'))
            os.environ['PIP_CACHE_DIR'] = cache_paths.get('pip_cache', str(project_root / '.cache' / 'pip_cache'))
            
            # Get model ID from config if not provided
            if model_id is None:
                model_id = config.get('models', {}).get('ai_model_id', 'microsoft/Phi-3-mini-4k-instruct')
            
            self.cache_dir = cache_paths.get('huggingface', str(project_root / '.cache' / 'huggingface'))
        else:
            # Fallback if config doesn't exist
            self.cache_dir = str(project_root / '.cache' / 'huggingface')
            if model_id is None:
                model_id = 'microsoft/Phi-3-mini-4k-instruct'
        
        self.model_id = model_id
        self.device = self._detect_device()
        self.available_optimizations = self._detect_optimizations()
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.is_quantized = False  # Track if model is quantized
        
        # Generation parameters - Optimized for quality and GPU usage
        self.generation_config = {
            "max_new_tokens": 384,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "do_sample": True,
            "pad_token_id": None,
        }
        
        self.logger.info(f"Platform: {self.platform}")
        self.logger.info(f"Device: {self.device}")
        self.logger.info(f"Available optimizations: {self.available_optimizations}")

    def _detect_device(self) -> str:
        """Detect optimal device for inference"""
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            self.logger.info(f"CUDA available: {gpu_count} GPU(s), {memory:.1f}GB memory")
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.logger.info("MPS (Apple Silicon) available")
            return "mps"
        else:
            self.logger.info("Using CPU")
            return "cpu"
    
    def _detect_optimizations(self) -> Dict[str, bool]:
        """Detect available optimizations"""
        optimizations = {
            'xformers': False,
            'flash_attn': False,
            'better_transformer': False,
            'bitsandbytes': False,
            'sdpa': False,
            'cuda_graphs': False
        }
        
        # Check for xformers
        try:
            import xformers
            optimizations['xformers'] = True
        except ImportError:
            pass
        
        # Check for flash-attention
        try:
            import flash_attn
            optimizations['flash_attn'] = True
        except ImportError:
            pass
        
        # Check for Better Transformer (PyTorch 2.0+)
        if hasattr(torch.nn.functional, 'scaled_dot_product_attention'):
            optimizations['sdpa'] = True
            optimizations['better_transformer'] = True
        
        # Check for bitsandbytes
        try:
            import bitsandbytes
            if self.device == "cuda":
                optimizations['bitsandbytes'] = True
        except ImportError:
            pass
        
        # CUDA graphs for maximum GPU utilization
        if self.device == "cuda":
            optimizations['cuda_graphs'] = True
        
        return optimizations
        
    def load_model(self, force_reload: bool = False) -> bool:
        """Load Phi-3 Mini model from cache"""
        if self.is_loaded and not force_reload:
            return True
        
        warnings.filterwarnings("ignore")
        
        try:
            self.logger.info(f"Loading Phi-3 Mini from cache: {self.cache_dir}")
            start_time = time.time()
            
            model_cache_path = Path(self.cache_dir) / "models--microsoft--Phi-3-mini-4k-instruct"
            
            if not model_cache_path.exists():
                self.logger.error(f"Model not found in cache at {model_cache_path}")
                return False
            
            self.logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                padding_side="left",
                cache_dir=self.cache_dir,
                local_files_only=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            
            self.generation_config["pad_token_id"] = self.tokenizer.pad_token_id
            
            # Load model based on device
            self.logger.info(f"Loading model for {self.device}...")
            
            if self.device == "cuda":
                self.model = self._load_cuda_model()
            elif self.device == "mps":
                self.model = self._load_mps_model()
            else:
                self.model = self._load_cpu_model()
            
            if self.model is None:
                self.logger.error("Failed to load model - model is None")
                return False
            
            # Apply post-load optimizations for maximum GPU usage (only if not quantized)
            if not self.is_quantized:
                self._apply_gpu_optimizations()
            
            load_time = time.time() - start_time
            self.logger.info(f" Model loaded successfully in {load_time:.2f}s")
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.is_loaded = False
            return False
            
    def _load_cuda_model(self):
        """Load model optimized for CUDA with 4-bit quantization"""
        import torch
        
        # Check available GPU memory
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        self.logger.info(f"Available GPU memory: {gpu_memory:.1f}GB")
        
        # ALWAYS use eager for Phi-3 (it doesn't support SDPA yet)
        attn_implementation = "eager"
        self.logger.info("Using eager attention (Phi-3 requirement)")
        
        # Try 4-bit quantization first (best for 6GB GPU)
        if self.available_optimizations['bitsandbytes']:
            try:
                # Use 4-bit quantization - this reduces model from ~7.6GB to ~2GB
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True, 
                    bnb_4bit_quant_type="nf4",  # Normal Float 4 quantization
                    bnb_4bit_compute_dtype=torch.float16,  # Compute in FP16
                    bnb_4bit_use_double_quant=True,  # Double quantization for more compression
                )
                
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    quantization_config=bnb_config,
                    trust_remote_code=True,
                    cache_dir=self.cache_dir,
                    local_files_only=True,
                    attn_implementation=attn_implementation
                )
                
                self.logger.info(" Loaded with 4-bit quantization on GPU (~2GB VRAM usage)")
                self.is_quantized = True  # Mark as quantized
                
                model.config.use_cache = True
                              
                return model
                
            except Exception as e:
                self.logger.error(f"4-bit quantization failed: {e}")
                # Fall through to FP16 loading
        
        # Fallback to FP16 if quantization failed or unavailable
        try:
            self.logger.warning("Loading without quantization (will use more VRAM)")
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map={'': 0},  # Only use device_map without quantization
                trust_remote_code=True,
                torch_dtype=torch.float16,
                cache_dir=self.cache_dir,
                local_files_only=True,
                attn_implementation=attn_implementation,
                low_cpu_mem_usage=True
            )
            self.logger.info("Loaded with FP16 entirely on GPU")
            
            # Enable KV cache for faster generation
            model.config.use_cache = True
            self.is_quantized = False
            
            # Enable xformers only for non-quantized models
            if self.available_optimizations['xformers']:
                try:
                    if hasattr(model, 'enable_xformers_memory_efficient_attention'):
                        model.enable_xformers_memory_efficient_attention()
                        self.logger.info("Enabled xFormers memory efficient attention")
                except Exception as e:
                    self.logger.debug(f"xFormers not enabled: {e}")
            
            return model
            
        except Exception as e:
            self.logger.error(f"FP16 loading failed: {e}")
            
            # Last resort fallback
            try:
                self.logger.info("Attempting fallback GPU loading...")
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    device_map="auto",  # Let it figure out the best mapping
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    cache_dir=self.cache_dir,
                    local_files_only=True,
                    attn_implementation="eager",  # Always eager for Phi-3
                    low_cpu_mem_usage=True
                )
                self.logger.warning("Using automatic device mapping (may use some CPU)")
                model.config.use_cache = True
                self.is_quantized = False
                return model
            except Exception as e2:
                self.logger.error(f"All loading methods failed: {e2}")
                return None
    
    def _apply_gpu_optimizations(self):
        """Apply optimizations for maximum GPU utilization (only for non-quantized models)"""
        if self.model is None or self.device != "cuda" or self.is_quantized:
            return
        
        # Set model to eval mode
        self.model.eval()
        
        # Enable CUDA optimizations
        if torch.cuda.is_available():
            # Enable TF32 for Ampere GPUs (3000 series and newer)
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Enable cudnn benchmarking for faster convolutions
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            
            # Set CUDA to use fastest algorithms
            torch.cuda.set_device(0)
            
            self.logger.info("Applied CUDA optimizations for maximum GPU utilization")
            
    def _load_mps_model(self):
        """Load model optimized for Apple Silicon"""
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                local_files_only=True,
                attn_implementation="eager"
            )
            model.config.use_cache = True
            self.is_quantized = False
            return model.to("mps")
        except Exception as e:
            self.logger.error(f"MPS model loading failed: {e}")
            raise
    
    def _load_cpu_model(self):
        """Load model for CPU inference"""
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                local_files_only=True,
                attn_implementation="eager"
            )
            
            # Enable CPU optimizations
            if hasattr(torch, 'set_num_threads'):
                import multiprocessing
                torch.set_num_threads(multiprocessing.cpu_count())
            
            model.config.use_cache = True
            self.is_quantized = False
            return model
        except Exception as e:
            self.logger.error(f"CPU model loading failed: {e}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text with maximum GPU utilization"""
        if not self.is_loaded:
            if not self.load_model():
                return "Error: Failed to load model"
        
        try:
            
            # Set random seed if not provided
            if 'seed' not in kwargs:
                seed = random.randint(0, 2**32 - 1)
                torch.manual_seed(seed)
                if self.device == "cuda":
                    torch.cuda.manual_seed(seed)

            default_temp = 0.75 if 'temperature' not in kwargs else kwargs.get('temperature')

            # Optimized generation config for GPU utilization
            gen_config = {
                'max_new_tokens': min(kwargs.get('max_new_tokens', 256), 512),
                'temperature': default_temp,  
                'do_sample': True,
                'top_p': 0.92, 
                'top_k': 100,  
                'repetition_penalty': 1.15,  
                'num_beams': 1,
                'use_cache': True,
                'pad_token_id': self.tokenizer.pad_token_id,
                'eos_token_id': self.tokenizer.eos_token_id,
                'do_sample': True,  
            }
            
            self.logger.info(f"Generating with max_tokens={gen_config['max_new_tokens']}")
            
            # Tokenize with optimal settings
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
                padding=True,  # Changed to True to ensure attention_mask is created
                return_attention_mask=True  # Explicitly request attention mask
            )
            
            # Move inputs to the same device as the model
            if self.device == "cuda":
                # Get the device of the model (it's already on the right device if using 4-bit)
                model_device = next(self.model.parameters()).device
                inputs = {k: v.to(model_device) for k, v in inputs.items()}
                
                # Warmup GPU if first run (helps with consistent timing)
                if not hasattr(self, '_warmed_up'):
                    with torch.no_grad():
                        # Don't use AMP with 4-bit models
                        if self.is_quantized:
                            _ = self.model.generate(
                                input_ids=inputs['input_ids'][:, :10],
                                attention_mask=torch.ones_like(inputs['input_ids'][:, :10]),
                                max_new_tokens=1
                            )
                        else:
                            with torch.cuda.amp.autocast(dtype=torch.float16):
                                _ = self.model.generate(
                                    input_ids=inputs['input_ids'][:, :10],
                                    attention_mask=torch.ones_like(inputs['input_ids'][:, :10]),
                                    max_new_tokens=1
                                )
                    self._warmed_up = True
                    torch.cuda.synchronize()
            elif self.device == "mps":
                device = torch.device("mps")
                inputs = {k: v.to(device) for k, v in inputs.items()}
            else:
                device = torch.device("cpu")
                inputs = {k: v.to(device) for k, v in inputs.items()}
            
            start_time = time.time()
            
            # Generate with GPU optimization
            self.model.eval()
            
            with torch.no_grad():
                if self.device == "cuda":
                    # Don't use AMP with 4-bit quantized models
                    if self.is_quantized:
                        outputs = self.model.generate(
                            input_ids=inputs['input_ids'],
                            attention_mask=inputs['attention_mask'],
                            **gen_config
                        )
                    else:
                        # Use AMP only for non-quantized models
                        with torch.cuda.amp.autocast(dtype=torch.float16):
                            outputs = self.model.generate(
                                input_ids=inputs['input_ids'],
                                attention_mask=inputs['attention_mask'],
                                **gen_config
                            )
                    
                    # Synchronize to get accurate timing
                    torch.cuda.synchronize()
                else:
                    # Standard generation for MPS/CPU
                    outputs = self.model.generate(
                        input_ids=inputs['input_ids'],
                        attention_mask=inputs['attention_mask'],
                        **gen_config
                    )
            
            generation_time = time.time() - start_time
            
            # Decode
            new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
            response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
            
            tokens_per_second = len(new_tokens) / generation_time
            self.logger.info(f"Generated {len(new_tokens)} tokens in {generation_time:.2f}s ({tokens_per_second:.1f} tok/s)")
            
            # Don't clear cache between generations for better performance
            # Only clear if memory is getting critically full
            if self.device == "cuda" and torch.cuda.is_available():
                memory_usage = torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory
                if memory_usage > 0.95:  # Only if >95% full
                    torch.cuda.empty_cache()
                    self.logger.info(f"Cleared cache due to high memory usage: {memory_usage:.1%}")
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return f"Error generating response: {str(e)}"
    
    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Generate with system and user prompts"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        return self.generate(formatted_prompt, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and status"""
        info = {
            "platform": self.platform,
            "model_id": self.model_id,
            "device": self.device,
            "is_loaded": self.is_loaded,
            "is_quantized": self.is_quantized,
            "quantization_type": "4-bit (NF4)" if self.is_quantized else "None",
            "tokenizer_loaded": self.tokenizer is not None,
            "optimizations": self.available_optimizations,
            "cache_dir": self.cache_dir
        }
        
        if self.is_loaded and self.device == "cuda" and torch.cuda.is_available():
            info.update({
                "gpu_memory_allocated_gb": torch.cuda.memory_allocated() / 1024**3,
                "gpu_memory_reserved_gb": torch.cuda.memory_reserved() / 1024**3,
                "gpu_memory_usage_pct": (torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory) * 100
            })
        
        return info
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        self.is_loaded = False
        self.is_quantized = False
        
        # Safe cleanup
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        gc.collect()
        self.logger.info("Model unloaded")

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'model') and self.model is not None:
            try:
                self.unload_model()
            except:
                pass
            


            