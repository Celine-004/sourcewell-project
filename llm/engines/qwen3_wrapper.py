"""
Qwen3-4B Model Wrapper - Optimized with 4-bit quantization
"""
import os
import json
import torch
import gc
import time
import random
import logging
import platform
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from typing import Dict, Any, Optional
import warnings

warnings.filterwarnings("ignore", message=".*torch_dtype.*deprecated.*")
warnings.filterwarnings("ignore", message=".*flash-attention.*")
warnings.filterwarnings("ignore", message=".*TRANSFORMERS_CACHE.*")


class Qwen3Wrapper:
    """Wrapper for Qwen3-4B model optimized for GPU inference with 4-bit quantization"""

    def __init__(self, model_id: str = None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.platform = platform.system().lower()
        self.is_windows = self.platform == 'windows'
        self.is_linux = self.platform == 'linux'
        self.is_mac = self.platform == 'darwin'

        project_root = Path(__file__).resolve().parents[2]
        config_file = project_root / "sourcewell_config.json"

        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)

            cache_paths = config.get('cache_paths', {})
            os.environ.pop('TRANSFORMERS_CACHE', None)
            os.environ['HF_HOME'] = cache_paths.get('huggingface', str(project_root / '.cache' / 'huggingface'))
            os.environ['TEMP'] = cache_paths.get('temp', str(project_root / '.cache' / 'temp'))
            os.environ['TMP'] = cache_paths.get('temp', str(project_root / '.cache' / 'temp'))
            os.environ['PIP_CACHE_DIR'] = cache_paths.get('pip_cache', str(project_root / '.cache' / 'pip_cache'))

            if model_id is None:
                model_id = config.get('models', {}).get('ai_model_id', 'Qwen/Qwen3-4B')

            self.cache_dir = cache_paths.get('huggingface', str(project_root / '.cache' / 'huggingface'))
        else:
            self.cache_dir = str(project_root / '.cache' / 'huggingface')
            if model_id is None:
                model_id = 'Qwen/Qwen3-4B'

        self.model_id = model_id
        self.device = self._detect_device()
        self.available_optimizations = self._detect_optimizations()
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.is_quantized = False

        # Generation parameters tuned for Qwen3
        self.generation_config = {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "do_sample": True,
            "pad_token_id": None,
        }

        self.logger.info(f"Qwen3Wrapper initialized")
        self.logger.info(f"Platform: {self.platform} | Device: {self.device}")
        self.logger.info(f"Model: {self.model_id}")
        self.logger.info(f"Available optimizations: {self.available_optimizations}")

    def _detect_device(self) -> str:
        """Detect optimal device for inference"""
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            memory = torch.cuda.get_device_properties(0).total_mem / 1024**3
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
            'flash_attn': False,
            'sdpa': False,
            'bitsandbytes': False,
        }

        try:
            import flash_attn
            optimizations['flash_attn'] = True
        except ImportError:
            pass

        if hasattr(torch.nn.functional, 'scaled_dot_product_attention'):
            optimizations['sdpa'] = True

        try:
            import bitsandbytes
            if self.device == "cuda":
                optimizations['bitsandbytes'] = True
        except ImportError:
            pass

        return optimizations

    def _select_attention(self) -> str:
        """Select best attention implementation for Qwen3"""
        if self.available_optimizations['flash_attn']:
            self.logger.info("Using flash_attention_2")
            return "flash_attention_2"
        elif self.available_optimizations['sdpa']:
            self.logger.info("Using SDPA attention")
            return "sdpa"
        else:
            self.logger.info("Using eager attention (fallback)")
            return "eager"

    def load_model(self, force_reload: bool = False) -> bool:
        """Load Qwen3 model from cache"""
        if self.is_loaded and not force_reload:
            return True

        warnings.filterwarnings("ignore")

        try:
            self.logger.info(f"Loading Qwen3 from: {self.cache_dir}")
            start_time = time.time()

            # Load tokenizer
            self.logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                padding_side="left",
                cache_dir=self.cache_dir
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

            if not self.is_quantized:
                self._apply_gpu_optimizations()

            load_time = time.time() - start_time
            self.logger.info(f"Qwen3 loaded successfully in {load_time:.2f}s")

            if self.device == "cuda":
                vram = torch.cuda.memory_allocated() / 1024**3
                self.logger.info(f"VRAM usage: {vram:.1f} GB")

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
        gpu_memory = torch.cuda.get_device_properties(0).total_mem / (1024**3)
        self.logger.info(f"Available GPU memory: {gpu_memory:.1f}GB")

        attn_impl = self._select_attention()

        # 4-bit quantization (primary path)
        if self.available_optimizations['bitsandbytes']:
            try:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                )

                model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    quantization_config=bnb_config,
                    trust_remote_code=True,
                    cache_dir=self.cache_dir,
                    attn_implementation=attn_impl
                )

                self.logger.info("Loaded with 4-bit quantization on GPU")
                self.is_quantized = True
                model.config.use_cache = True
                return model

            except Exception as e:
                self.logger.error(f"4-bit quantization failed: {e}")

        # FP16 fallback
        try:
            self.logger.warning("Loading without quantization (higher VRAM usage)")
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
                cache_dir=self.cache_dir,
                attn_implementation=attn_impl,
                low_cpu_mem_usage=True
            )
            self.logger.info("Loaded with FP16 on GPU")
            model.config.use_cache = True
            self.is_quantized = False
            return model

        except Exception as e:
            self.logger.error(f"All CUDA loading methods failed: {e}")
            return None

    def _load_mps_model(self):
        """Load model for Apple Silicon"""
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                attn_implementation="eager"
            )
            model.config.use_cache = True
            self.is_quantized = False
            return model.to("mps")
        except Exception as e:
            self.logger.error(f"MPS loading failed: {e}")
            return None

    def _load_cpu_model(self):
        """Load model for CPU inference"""
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                cache_dir=self.cache_dir,
                attn_implementation="eager"
            )

            if hasattr(torch, 'set_num_threads'):
                import multiprocessing
                torch.set_num_threads(multiprocessing.cpu_count())

            model.config.use_cache = True
            self.is_quantized = False
            return model
        except Exception as e:
            self.logger.error(f"CPU loading failed: {e}")
            return None

    def _apply_gpu_optimizations(self):
        """Apply CUDA optimizations for non-quantized models"""
        if self.model is None or self.device != "cuda" or self.is_quantized:
            return

        self.model.eval()

        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            torch.cuda.set_device(0)
            self.logger.info("Applied CUDA optimizations")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a raw prompt string"""
        if not self.is_loaded:
            if not self.load_model():
                return "Error: Failed to load model"

        try:
            if 'seed' not in kwargs:
                seed = random.randint(0, 2**32 - 1)
                torch.manual_seed(seed)
                if self.device == "cuda":
                    torch.cuda.manual_seed(seed)

            gen_config = {
                'max_new_tokens': min(kwargs.get('max_new_tokens', 512), 768),
                'temperature': kwargs.get('temperature', 0.7),
                'do_sample': True,
                'top_p': kwargs.get('top_p', 0.9),
                'top_k': kwargs.get('top_k', 50),
                'repetition_penalty': kwargs.get('repetition_penalty', 1.15),
                'num_beams': 1,
                'use_cache': True,
                'pad_token_id': self.tokenizer.pad_token_id,
                'eos_token_id': self.tokenizer.eos_token_id,
            }

            self.logger.info(f"Generating with max_tokens={gen_config['max_new_tokens']}")

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=3072,  # Qwen3 supports 32K but we limit for VRAM
                padding=True,
                return_attention_mask=True
            )

            # Move to model device
            model_device = next(self.model.parameters()).device
            inputs = {k: v.to(model_device) for k, v in inputs.items()}

            start_time = time.time()
            self.model.eval()

            with torch.no_grad():
                if self.device == "cuda" and not self.is_quantized:
                    with torch.cuda.amp.autocast(dtype=torch.float16):
                        outputs = self.model.generate(
                            input_ids=inputs['input_ids'],
                            attention_mask=inputs['attention_mask'],
                            **gen_config
                        )
                else:
                    outputs = self.model.generate(
                        input_ids=inputs['input_ids'],
                        attention_mask=inputs['attention_mask'],
                        **gen_config
                    )

                if self.device == "cuda":
                    torch.cuda.synchronize()

            generation_time = time.time() - start_time

            new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
            response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

            tokens_per_second = len(new_tokens) / generation_time if generation_time > 0 else 0
            self.logger.info(f"Generated {len(new_tokens)} tokens in {generation_time:.2f}s ({tokens_per_second:.1f} tok/s)")

            # Only clear VRAM cache if critically full
            if self.device == "cuda" and torch.cuda.is_available():
                usage = torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_mem
                if usage > 0.95:
                    torch.cuda.empty_cache()
                    self.logger.info(f"Cleared cache: {usage:.0%} VRAM used")

            return response.strip()

        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return f"Error generating response: {str(e)}"

    def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Generate using Qwen3 chat template with thinking disabled"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False  # Direct answers, no chain-of-thought
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
                "gpu_memory_usage_pct": (torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_mem) * 100
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

        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()

        gc.collect()
        self.logger.info("Qwen3 model unloaded")

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'model') and self.model is not None:
            try:
                self.unload_model()
            except:
                pass
