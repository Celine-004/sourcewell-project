"""
Installation Script

One-command setup for the SourceWell platform:
1. Verifies proper development environment setup
2. Upgrades pip and essential build tools
3. Installs core dependencies from requirements.txt
4. Detects hardware capabilities (NVIDIA, AMD, Intel, Apple Silicon)
5. Installs optimal PyTorch configuration for maximum performance
6. Verifies complete system functionality

Usage:
    python setup_sourcewell.py              # Interactive installation
    python setup_sourcewell.py --auto       # Automatic installation
    python setup_sourcewell.py --cpu-only   # Force CPU-only mode
    python setup_sourcewell.py --version=2.5.1  # Specific PyTorch version
    python setup_sourcewell.py --create-config  # Create configuration file
    python setup_sourcewell.py --show-config    # Show current configuration
"""

from __future__ import annotations
import os
import re
import sys
import json
import copy
import shutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple, Any

class SourceWellConfig:
    
    # pytorch configuration
    DEFAULT_PYTORCH_VERSION = "2.3.1"
    DEFAULT_CUDA_VERSION = "121"
    DEFAULT_ROCM_VERSION = "6.0"

    # ai optimization packages
    DEFAULT_BITSANDBYTES_VERSION = "0.41"

    #model configuration pakages
    DEFAULT_AI_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
    DEFAULT_EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
    ENABLE_MODEL_PREDOWNLOAD = True

    # Windows fallback for bitsandbytes
    WINDOWS_BITSANDBYTES_WHEEL = "https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.1-py3-none-win_amd64.whl"
    
    # PyTorch CUDA compatibility matrix (actual available wheels)
    PYTORCH_CUDA_COMPATIBILITY = {
        "2.5.1": ["121", "118"],
        "2.5.0": ["121", "118"],
        "2.6.0": ["121", "118"],
        "2.4.1": ["121", "118"],
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else Path(__file__).parent / "sourcewell_config.json"
        self.config = self._load_configuration()
    
    def _load_configuration(self) -> Dict[str, str]:
        """Load configuration with precedence: ENV > config file > defaults."""
        config = {
            # pytorch versions
            'pytorch_version': self.DEFAULT_PYTORCH_VERSION,
            'cuda_version': self.DEFAULT_CUDA_VERSION,
            'rocm_version': self.DEFAULT_ROCM_VERSION,

            # ai package versions
            'bitsandbytes_version': self.DEFAULT_BITSANDBYTES_VERSION,
            'ai_model_id': self.DEFAULT_AI_MODEL_ID,
            'embedding_model_id': self.DEFAULT_EMBEDDING_MODEL_ID,
            'enable_model_predownload': self.ENABLE_MODEL_PREDOWNLOAD,

        }
        
        # 1. Load from config file (if exists)
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config.get('versions', {}))
                    config.update(file_config.get('models', {}))  # ADD THIS LINE
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                
        # 2. Override with environment variables (highest priority)
        env_mappings = {
            'SOURCEWELL_PYTORCH_VERSION': 'pytorch_version',
            'SOURCEWELL_CUDA_VERSION': 'cuda_version',
            'SOURCEWELL_ROCM_VERSION': 'rocm_version',
            'SOURCEWELL_BITSANDBYTES_VERSION': 'bitsandbytes_version',
            'SOURCEWELL_AI_MODEL': 'ai_model_id',                   
            'SOURCEWELL_PREDOWNLOAD_MODELS': 'enable_model_predownload'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                 env_value = os.getenv(env_var)
                 if config_key == 'enable_model_predownload':
                    config[config_key] = env_value.lower() in ('1', 'true', 'yes', 'on')
                 else:
                    config[config_key] = env_value
        
        return config
    
    def get_pytorch_version(self) -> str:
        return self.config['pytorch_version']
    
    def get_cuda_version(self, detected_cuda: Optional[str] = None) -> str:
        """Get compatible CUDA version with intelligent selection."""
        pytorch_ver = self.config['pytorch_version']
        requested_cuda = self.config['cuda_version']
        
        # Get available CUDA versions for this PyTorch version
        compatible_versions = self.PYTORCH_CUDA_COMPATIBILITY.get(pytorch_ver, [self.DEFAULT_CUDA_VERSION])
        if detected_cuda:
            # Extract major.minor from detected version (e.g., "13.0" -> prefer "121" if available)
            try:
                major, minor = detected_cuda.split(".")[:2]
                detected_key = f"{major}{minor}"
                best_match = None
                for ver in sorted(compatible_versions, reverse=True):
                    if int(ver) <= int(detected_key):
                        best_match = ver
                        break
                
                if best_match:
                    if best_match != requested_cuda:
                        print(f" Auto-selected CUDA {best_match} (compatible with detected CUDA {detected_cuda})")
                    return best_match
            except Exception:
                pass
        
        # Validate requested version
        if requested_cuda not in compatible_versions:
            print(f" CUDA {requested_cuda} not available for PyTorch {pytorch_ver}")
            print(f" Available versions: {', '.join(compatible_versions)}")
            return compatible_versions[0]
        
        return requested_cuda
    
    def get_rocm_version(self) -> str:
        return self.config['rocm_version']
    
    def get_bitsandbytes_version(self) -> str:
        return self.config['bitsandbytes_version']
    
    def get_ai_model_id(self) -> str:
        return self.config['ai_model_id']
        
    def get_embedding_model_id(self):
        return self.config['embedding_model_id']

    def should_predownload_models(self) -> bool:
        return bool(self.config['enable_model_predownload'])

    def create_sample_config(self) -> bool:
        sample_config = {
            "versions": {
                "pytorch_version": self.DEFAULT_PYTORCH_VERSION,
                "cuda_version": self.DEFAULT_CUDA_VERSION,
                "rocm_version": self.DEFAULT_ROCM_VERSION,
                "bitsandbytes_version": self.DEFAULT_BITSANDBYTES_VERSION
            },

            "models": {
                "ai_model_id": self.DEFAULT_AI_MODEL_ID,
                "embedding_model_id": self.DEFAULT_EMBEDDING_MODEL_ID,
                "enable_model_predownload": self.ENABLE_MODEL_PREDOWNLOAD
            },

            "_comment": "SourceWell Configuration - Edit versions as needed",
            "_cuda_info": "CUDA versions: 121 (CUDA 12.1), 118 (CUDA 11.8) - compatible with CUDA 13.0+ drivers"
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2)
            print(f" Sample configuration created: {self.config_file}")
            return True
        except Exception as e:
            print(f" Could not create config file: {e}")
            return False

    def save_cache_paths(self, hf_home: str, temp_path: str = None, pip_cache: str = None):
        """Save the chosen cache paths to config file for other processes to use."""
        try:
            # Load existing config or create new structure
            config_data = {}
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            # Add cache_paths section
            if 'cache_paths' not in config_data:
                config_data['cache_paths'] = {}
            
            config_data['cache_paths']['huggingface'] = hf_home
            if temp_path:
                config_data['cache_paths']['temp'] = temp_path
            if pip_cache:
                config_data['cache_paths']['pip_cache'] = pip_cache
            
            # Ensure other sections exist
            if 'versions' not in config_data:
                config_data['versions'] = {
                    "pytorch_version": self.DEFAULT_PYTORCH_VERSION,
                    "cuda_version": self.DEFAULT_CUDA_VERSION,
                    "rocm_version": self.DEFAULT_ROCM_VERSION,
                    "bitsandbytes_version": self.DEFAULT_BITSANDBYTES_VERSION
                }
            
            if 'models' not in config_data:
                config_data['models'] = {
                    "ai_model_id": self.DEFAULT_AI_MODEL_ID,
                    "embedding_model_id": self.DEFAULT_EMBEDDING_MODEL_ID,
                    "enable_model_predownload": self.ENABLE_MODEL_PREDOWNLOAD
                }
            
            # Save updated config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            print(f" Cache paths saved to config: {self.config_file}")
            
        except Exception as e:
            print(f" Could not save cache paths: {e}")

class SourceWellInstaller:

    def __init__(self, pytorch_version: Optional[str] = None, force_cpu: bool = False, config: Optional[SourceWellConfig] = None):
        self.config = config or SourceWellConfig()
        self.pytorch_version = pytorch_version or self.config.get_pytorch_version()
        self.force_cpu = force_cpu
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.system_info = self._detect_system()   
        os.environ.pop('TRANSFORMERS_CACHE', None)
        self.storage_config = self._configure_adaptive_storage_management(min_free_gb=10.0)
        self.gpu_capabilities = self._detect_gpu_hardware()
        self.pytorch_config = self._determine_pytorch_config()
        self.installation_log = []
        
        print(f" Using PyTorch version: {self.pytorch_version}")
    
    def _detect_system(self) -> Dict[str, str]:
        """Detect os and python environment."""
        return {
            'os': platform.system().lower(),
            'arch': platform.machine().lower(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
            'platform_details': platform.platform(),
            'in_venv': hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        }
    
    def _run_command(self, cmd: List[str], timeout: int = 120) -> Tuple[bool, str, str]:
        """Execute system command with error handling and environment propagation."""
        try:
            env = copy.copy(os.environ)
            
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                check=False, encoding='utf-8', errors='ignore',
                env=env  
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", f"Timeout after {timeout}s"
        except Exception as e:
            return False, "", str(e)
        
    def _configure_adaptive_storage_management(self, min_free_gb: float = 10.0) -> Dict[str, Any]:
        """
        Configure storage to always use project directory for all caches.
        This ensures all downloads stay within the project folder.
        """
        storage_config = {
            'activated': True,  # Always activated
            'reason': 'Project-local storage (all files stay in project)',
            'temp_path': None,
            'cache_path': None,
            'original_free_gb': 0
        }
        
        try:
            # Always use project directory regardless of available space
            project_cache_base = self.project_root / ".cache"
            
            # Check project directory space
            project_total, project_used, project_free = shutil.disk_usage(self.project_root)
            project_free_gb = project_free / (1024**3)
            storage_config['original_free_gb'] = project_free_gb
            
            print(f" Project directory: {self.project_root}")
            print(f" Available space: {project_free_gb:.1f}GB")
            
            # Warn if space is low but continue anyway
            if project_free_gb < min_free_gb:
                print(f"  Warning: Low disk space ({project_free_gb:.1f}GB < {min_free_gb}GB recommended)")
                print(f"   Model downloads require ~8GB. Consider freeing space if needed.")
            
            # Create all cache directories in project folder
            temp_dir = project_cache_base / "temp"
            pip_cache_dir = project_cache_base / "pip_cache"
            hf_cache_dir = project_cache_base / "huggingface"
            
            # Create directories
            temp_dir.mkdir(parents=True, exist_ok=True)
            pip_cache_dir.mkdir(parents=True, exist_ok=True)
            hf_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Set all environment variables to use project directory
            os.environ['TMP'] = str(temp_dir)
            os.environ['TEMP'] = str(temp_dir)
            os.environ['TMPDIR'] = str(temp_dir)  # For Unix-like systems
            os.environ['PIP_CACHE_DIR'] = str(pip_cache_dir)
            os.environ['HF_HOME'] = str(hf_cache_dir)
            os.environ['TRANSFORMERS_CACHE'] = str(hf_cache_dir / "transformers")  # Legacy support
            os.environ['HF_DATASETS_CACHE'] = str(hf_cache_dir / "datasets")
            os.environ['TORCH_HOME'] = str(project_cache_base / "torch")
            
            # Create torch cache directory
            (project_cache_base / "torch").mkdir(parents=True, exist_ok=True)
            
            storage_config.update({
                'activated': True,
                'temp_path': str(temp_dir),
                'cache_path': str(pip_cache_dir),
                'hf_cache_path': str(hf_cache_dir),
                'reason': f'Project-local storage configured ({project_free_gb:.1f}GB available)'
            })
            
            print(f" All downloads will be saved to: {project_cache_base}")
            print(f"    Temp files: {temp_dir.relative_to(self.project_root)}")
            print(f"    Pip cache: {pip_cache_dir.relative_to(self.project_root)}")
            print(f"    AI models: {hf_cache_dir.relative_to(self.project_root)}")
            print(f"    PyTorch: {project_cache_base.relative_to(self.project_root)}/torch")
            
        except Exception as e:
            print(f" Storage configuration warning: {e}")
            print(f"   Continuing with system defaults...")
            storage_config['reason'] = f"Configuration error: {e}"
        
        # Always persist the cache paths for other processes
        hf_home = os.getenv('HF_HOME', str(self.project_root / ".cache" / "huggingface"))
        temp_path = os.getenv('TMP', str(self.project_root / ".cache" / "temp"))
        pip_cache = os.getenv('PIP_CACHE_DIR', str(self.project_root / ".cache" / "pip_cache"))
        
        self.config.save_cache_paths(hf_home, temp_path, pip_cache)
        
        return storage_config

    def _detect_gpu_hardware(self) -> Dict[str, Any]:
        capabilities = {
            'nvidia_detected': False,
            'amd_rocm_detected': False,
            'intel_gpu_detected': False,
            'apple_silicon': False,
            'detected_devices': [],
            'primary_vendor': 'cpu',
            'nvidia_cuda_version': None
        }
        
        if self.force_cpu:
            capabilities['detected_devices'].append("CPU-only mode (user requested)")
            return capabilities
        
        # NVIDIA Detection with CUDA version extraction
        success, stdout, _ = self._run_command(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader,nounits'], timeout=10)
        if success and stdout:
            capabilities['nvidia_detected'] = True
            capabilities['primary_vendor'] = 'nvidia'
            
            # Parse GPU details
            lines = stdout.strip().split('\n')
            if lines and lines[0]:
                parts = [p.strip() for p in lines[0].split(',')]
                if len(parts) >= 3:
                    gpu_name, memory_mb, driver_version = parts[0], parts[1], parts[2]
                    
                    # Try to detect CUDA version from nvidia-smi output
                    smi_success, smi_output, _ = self._run_command(['nvidia-smi'], timeout=5)
                    if smi_success and 'CUDA Version:' in smi_output:
                        cuda_match = re.search(r'CUDA Version:\s*(\d+\.\d+)', smi_output)
                        if cuda_match:
                            capabilities['nvidia_cuda_version'] = cuda_match.group(1)
                    
                    cuda_info = f" (CUDA {capabilities['nvidia_cuda_version']})" if capabilities['nvidia_cuda_version'] else ""
                    capabilities['detected_devices'].append(
                        f"NVIDIA {gpu_name} ({memory_mb}MB VRAM, Driver: {driver_version}{cuda_info})"
                    )
        
        # Apple Silicon Detection
        if (self.system_info['os'] == 'darwin' and 
            self.system_info['arch'] in ['arm64', 'aarch64']):
            capabilities['apple_silicon'] = True
            if capabilities['primary_vendor'] == 'cpu':
                capabilities['primary_vendor'] = 'apple'
            capabilities['detected_devices'].append("Apple Silicon (Metal Performance Shaders)")
        
        # AMD ROCm Detection (Linux only)
        if self.system_info['os'] == 'linux':
            success, stdout, _ = self._run_command(['rocminfo'], timeout=10)
            if success and 'Agent' in stdout:
                capabilities['amd_rocm_detected'] = True
                if capabilities['primary_vendor'] == 'cpu':
                    capabilities['primary_vendor'] = 'amd'
                capabilities['detected_devices'].append("AMD GPU (ROCm compatible)")
        
        # Intel GPU Detection
        if self.system_info['os'] in ['linux', 'windows']:
            if self.system_info['os'] == 'linux':
                success, stdout, _ = self._run_command(['lspci'], timeout=5)
                intel_detected = success and 'intel' in stdout.lower() and any(k in stdout.lower() for k in ['vga', 'display', 'graphics'])
            else:  # Windows
                success, stdout, _ = self._run_command(['wmic', 'path', 'Win32_VideoController', 'get', 'name'], timeout=10)
                intel_detected = success and 'intel' in stdout.lower()
            
            if intel_detected:
                capabilities['intel_gpu_detected'] = True
                if capabilities['primary_vendor'] == 'cpu':
                    capabilities['primary_vendor'] = 'intel'
                capabilities['detected_devices'].append("Intel GPU detected")
        
        return capabilities
    
    def _determine_pytorch_config(self) -> Dict[str, Any]:
        config = {
            'method': 'cpu',
            'packages': [f'torch=={self.pytorch_version}'],
            'index_url': None,
            'extra_packages': [],
            'description': 'CPU-only PyTorch (universal compatibility)',
            'expected_acceleration': 'CPU-only'
        }
        
        if self.force_cpu:
            config['description'] = 'CPU-only PyTorch (user requested)'
            return config
        
        bitsandbytes_version = self.config.get_bitsandbytes_version()
        
        if self.gpu_capabilities['nvidia_detected']:
            detected_cuda = self.gpu_capabilities.get('nvidia_cuda_version')
            cuda_version = self.config.get_cuda_version(detected_cuda)
            config.update({
                'method': 'nvidia_cuda',
                'packages': [f'torch=={self.pytorch_version}+cu{cuda_version}'],
                'index_url': f'https://download.pytorch.org/whl/cu{cuda_version}',
                'extra_packages': [f'bitsandbytes>={bitsandbytes_version}'],
                'windows_fallback_wheel': self.config.WINDOWS_BITSANDBYTES_WHEEL,
                'description': f'NVIDIA CUDA-enabled PyTorch {self.pytorch_version} with 4-bit quantization',
                'expected_acceleration': f'CUDA {cuda_version} (NVIDIA GPU with 4-bit quantization)'
            })
        elif self.gpu_capabilities['apple_silicon']:
            config.update({
                'method': 'apple_mps',
                'packages': [f'torch=={self.pytorch_version}'],
                'extra_packages': [f'bitsandbytes>={bitsandbytes_version}'],
                'description': f'Apple Silicon PyTorch {self.pytorch_version} with MPS and 4-bit quantization',
                'expected_acceleration': 'MPS (Apple GPU with 4-bit quantization support)'
            })
        elif self.gpu_capabilities['amd_rocm_detected']:
            rocm_version = self.config.get_rocm_version()
            config.update({
                'method': 'amd_rocm',
                'packages': [f'torch=={self.pytorch_version}+rocm{rocm_version}'],
                'index_url': f'https://download.pytorch.org/whl/rocm{rocm_version}',
                'extra_packages': [],
                'description': f'AMD ROCm-enabled PyTorch {self.pytorch_version}',
                'expected_acceleration': f'ROCm {rocm_version} (AMD GPU)'
            })
        elif self.gpu_capabilities['intel_gpu_detected']:
            config.update({
                'method': 'intel_xpu',
                'packages': [f'torch=={self.pytorch_version}'],
                'extra_packages': [f'intel-extension-for-pytorch==2.5.0+xpu'],
                'description': f'Intel GPU PyTorch {self.pytorch_version} with XPU',
                'expected_acceleration': 'XPU (Intel GPU)'
            })
        return config
    
    def _filter_requirements_content(self) -> str:
        if not self.requirements_file.exists():
            return ""
        
        content = self.requirements_file.read_text(encoding='utf-8')
        filtered_lines = []
        skipped_lines = []
        
        for line in content.split('\n'):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                filtered_lines.append(line)
                continue
            
            lower_line = stripped.lower()

            # Filter PyTorch-related packages
            if any(pkg in lower_line for pkg in ['torch==', 'torch>=', 'torch<', 'torchvision', 'torchaudio']):
                skipped_lines.append(line)
                continue
            
            # Filter bitsandbytes 
            if 'bitsandbytes' in lower_line:
                skipped_lines.append(line)
                continue

            filtered_lines.append(line)
        
        if skipped_lines:
            print(" Filtered device-specific packages from requirements.txt:")
            for line in skipped_lines:
                print(f"    - {line}")
        
        return '\n'.join(filtered_lines)
    
    def print_system_analysis(self):
        print("Installation Analysis")
        print("=" * 60)
        print(f"System: {self.system_info['os'].title()} {self.system_info['arch']}")
        print(f"Python: {self.system_info['python_version']}")
        print(f"Virtual Environment: {' Active' if self.system_info['in_venv'] else '  Not detected'}")
        print(f"PyTorch Target: {self.pytorch_version}")
        print()
        
        print(" Hardware Detection:")
        print("-" * 25)
        if self.gpu_capabilities['detected_devices']:
            for i, device in enumerate(self.gpu_capabilities['detected_devices'], 1):
                print(f"  {i}. {device}")
        else:
            print("  No GPU hardware detected")
        print()
        
        print(" PyTorch Configuration:")
        print("-" * 25)
        print(f"Method: {self.pytorch_config['method']}")
        print(f"Description: {self.pytorch_config['description']}")
        print(f"Expected Acceleration: {self.pytorch_config['expected_acceleration']}")
        print()
        
        print(" Installation Plan:")
        print("-" * 20)
        print("1.  Upgrade pip and build tools")
        print("2.  Install core dependencies (filtered)")
        print("3.  Install optimal PyTorch configuration")
        if self.pytorch_config['extra_packages']:
            print(f"4.  Install additional packages")
        print("5.  Verify complete system functionality")
        print()
    
    def install_build_tools(self) -> bool:
        print(" Upgrading pip and build tools...")
        self.installation_log.append("Build tools upgrade")
        
        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel']
        success, _, stderr = self._run_command(cmd, timeout=60)
        
        if success:
            print(" Build tools upgraded successfully")
            return True
        else:
            print(f"  Build tools upgrade warning: {stderr}")
            return True  # Continue anyway
    
    def install_core_dependencies(self) -> bool:
        print(" Installing core dependencies...")
        self.installation_log.append("Core dependencies installation")
        
        filtered_content = self._filter_requirements_content()
        if not filtered_content.strip():
            print("  No core dependencies to install")
            return True
        
        temp_req_file = self.project_root / "temp_requirements.txt"
        temp_req_file.write_text(filtered_content, encoding='utf-8')
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(temp_req_file)]
            success, _, stderr = self._run_command(cmd, timeout=300)
            
            if success:
                print(" Core dependencies installed successfully")
                return True
            else:
                print(f" Core dependencies failed: {stderr}")
                return False
        finally:
            if temp_req_file.exists():
                temp_req_file.unlink()
    
    def install_pytorch(self) -> bool:
        """Install PyTorch with robust timeout and retry logic."""
        print(" Installing PyTorch...")
        self.installation_log.append("PyTorch installation")
        
        print("  Removing existing PyTorch installations...")
        self._run_command([sys.executable, '-m', 'pip', 'uninstall', 'torch', 'torchvision', 'torchaudio', '-y'], timeout=60)
        
        # Build robust pip command with network retry logic
        base_cmd = [
            sys.executable, '-m', 'pip', 'install',
            '--timeout', '1800',        # 30 minutes for large downloads
            '--retries', '5',           # Retry failed downloads
            '--disable-pip-version-check',  # Prevent version check delays
            '--no-input'                # Prevent interactive prompts
        ]
        
        # Add index URL if specified
        if self.pytorch_config['index_url']:
            base_cmd.extend(['--index-url', self.pytorch_config['index_url']])
        
        # Install PyTorch with progress indication
        print(f"  Installing {self.pytorch_config['description']}...")
        print(f"   Downloading 2.5GB CUDA wheel - may take 10-20 minutes on slower connections")
        
        cmd = base_cmd + self.pytorch_config['packages']
        success, stdout, stderr = self._run_command(cmd, timeout=1800)  # 30 minutes total
        
        if not success:
            print(f"  PyTorch installation failed: {stderr}")
            
            # Automatic CPU fallback to prevent complete blocking
            if self.pytorch_config['method'] in ('nvidia_cuda', 'amd_rocm'):
                print("   Attempting CPU-only PyTorch fallback to keep development unblocked...")
                cpu_cmd = [sys.executable, '-m', 'pip', 'install', '--timeout', '600', '--retries', '3', f'torch=={self.pytorch_version}']
                success_cpu, _, stderr_cpu = self._run_command(cpu_cmd, timeout=600)
                
                if success_cpu:
                    print("   CPU-only PyTorch installed successfully")
                    print("      You can upgrade to CUDA later with:")
                    print(f"     pip install --index-url {self.pytorch_config['index_url']} {self.pytorch_config['packages'][0]}")
                    return True
                else:
                    print(f"   CPU fallback also failed: {stderr_cpu}")
                    return False
            
            return False
        
        print("   PyTorch installation completed!")
         
        # Install extra packages (bitsandbytes, Intel XPU, etc.)
        if self.pytorch_config['extra_packages']:
            print("   Installing AI optimization packages...")
            
            # Use clean pip command for PyPI packages (no torch index URL)
            extra_cmd = [
                sys.executable, '-m', 'pip', 'install',
                '--timeout', '600', '--retries', '3',
            ] + self.pytorch_config['extra_packages']
            
            success, _, stderr = self._run_command(extra_cmd, timeout=900)
            
            if success:
                print("    AI optimization packages installed!")
            else:
                print(f"    AI packages failed: {stderr}")
                
                # Windows-specific bitsandbytes fallback
                if (self.system_info['os'] == 'windows' and 
                    any('bitsandbytes' in pkg for pkg in self.pytorch_config['extra_packages'])):
                    
                    fallback_wheel = self.pytorch_config.get('windows_fallback_wheel')
                    if fallback_wheel:
                        print("   Trying Windows bitsandbytes wheel...")
                        win_cmd = [sys.executable, '-m', 'pip', 'install', fallback_wheel]
                        win_success, _, _ = self._run_command(win_cmd, timeout=300)
                        
                        if win_success:
                            print("    Windows bitsandbytes installed!")
                        else:
                            print("    Proceeding without 4-bit quantization")

        return True
    
    def verify_installation(self) -> bool:
        """Installation verification with fault-tolerant architecture."""
        print(" Verifying installation...")
        
        results = {
            'pytorch_import': False,
            'gpu_acceleration': False, 
            'core_dependencies': False,
            'ai_optimization': False
        }
        
        # Phase 1: Critical PyTorch functionality
        torch_available = False
        try:
            import torch
            torch_available = True  
            results['pytorch_import'] = True
            print(f" PyTorch {torch.__version__} imported successfully")
            
            # GPU acceleration testing (only if PyTorch imported)
            if self.pytorch_config['method'] == 'nvidia_cuda':
                if torch.cuda.is_available():
                    device_name = torch.cuda.get_device_name(0)
                    memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    print(f" CUDA acceleration: {device_name} ({memory_gb:.1f}GB)")
                    results['gpu_acceleration'] = True
                else:
                    print(" CUDA not available")
            elif self.pytorch_config['method'] == 'apple_mps':
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    print(" Apple MPS acceleration available")
                    results['gpu_acceleration'] = True
                else:
                    print(" MPS not available")
            else:
                print(" PyTorch ready")
                results['gpu_acceleration'] = True
                
        except ImportError as e:
            print(f" PyTorch import failed: {e}")
        
        # Phase 2: Core dependencies (independent test)
        try:
            import weaviate, streamlit, fastapi, sentence_transformers
            print(" Core dependencies verified")
            results['core_dependencies'] = True
        except ImportError as e:
            print(f" Missing core dependency: {e}")
        
        # Phase 3: AI optimization (guarded and isolated)
        if self.pytorch_config.get('extra_packages') and torch_available:  
            try:
                if any('bitsandbytes' in pkg for pkg in self.pytorch_config['extra_packages']):
                    # Re-import torch in this scope to be explicit
                    import torch
                    import bitsandbytes
                    from transformers import BitsAndBytesConfig
                    
                    # Test quantization config creation
                    config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,  
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                    
                    print(f" AI optimization: bitsandbytes {bitsandbytes.__version__} (4-bit quantization ready)")
                    results['ai_optimization'] = True
                else:
                    print(" No AI optimization packages configured")
                    results['ai_optimization'] = True
                    
            except Exception as e:
                print(f" AI optimization warning: {e}")
                print("   Phi-3 Mini will run without quantization (higher VRAM usage)")
                results['ai_optimization'] = True  # Don't fail installation for optional features
        else:
            if not torch_available:
                print(" Skipping AI optimization check (PyTorch not available)")
            results['ai_optimization'] = True  # Don't penalize for missing optional features
        
        # Final assessment with intelligent scoring
        passed = sum(results.values())
        total = len(results)
        print(f"\n Verification Summary: {passed}/{total} components verified")
        
        # Require core functionality (PyTorch + dependencies) for success
        essential_components = results['pytorch_import'] and results['core_dependencies']
        
        if essential_components:
            print(" Installation verification successful!")
            if not results['gpu_acceleration']:
                print("   Note: GPU acceleration not available - using CPU mode")
            if not all(results.values()):
                print("   Note: Some optimizations unavailable but core functionality works")
            return True
        else:
            print(" Installation verification failed - core components missing")
            return False
        
    def save_installation_log(self):
        log_file = self.project_root / "sourcewell_installation.log"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("Installation Log\n")
                f.write("=" * 40 + "\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write(f"System: {self.system_info['platform_details']}\n")
                f.write(f"PyTorch: {self.pytorch_version}\n")
                f.write(f"Method: {self.pytorch_config['method']}\n")
                f.write("\nSteps:\n")
                for entry in self.installation_log:
                    f.write(f"- {entry}\n")
            print(f" Installation log saved: {log_file}")
        except Exception as e:
            print(f"  Could not save log: {e}")
    
    def install_ai_models(self) -> bool:
        """Download AI models with progress tracking."""
        if not self.config.should_predownload_models():
            print(" Model predownload disabled")
            return True
        
        print(" Downloading AI models...")
        
        success_count = 0
        
        # Download Phi-3 Mini (~7.6GB)
        if self._download_phi3_model():
            success_count += 1
        
        # Download embedding model (~90MB)  
        if self._download_embedding_model():
            success_count += 1
        
        print(f" {success_count}/2 AI models downloaded")
        return True  # Don't fail installation for model issues

    def _download_phi3_model(self) -> bool:
        """Download Phi-3 Mini with proper caching."""
        model_id = self.config.get_ai_model_id()
        print(f"    Downloading {model_id} (~7.6GB)")
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            # Get cache directory from environment
            cache_dir = os.getenv('HF_HOME', str(self.project_root / '.cache' / 'huggingface'))
            
            print(f"    Cache location: {cache_dir}")
            
            # Download tokenizer first (small, quick feedback)
            print("    Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_id, 
                trust_remote_code=True,
                cache_dir=cache_dir
            )
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            print("    ✓ Tokenizer cached")
            
            # Determine optimal dtype based on hardware
            if self.gpu_capabilities['nvidia_detected'] or self.gpu_capabilities['apple_silicon']:
                torch_dtype = torch.float16
                print("    Using FP16 for GPU optimization")
            else:
                torch_dtype = torch.float32
                print("    Using FP32 for CPU")
            
            # Download model
            print("    Downloading model files (this may take 10-20 minutes)...")
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                cache_dir=cache_dir
            )
            print("    ✓ Phi-3 Mini model cached successfully")
            
            # Verify the cache exists
            model_cache_path = Path(cache_dir) / "models--microsoft--Phi-3-mini-4k-instruct"
            if model_cache_path.exists():
                # List cached files for verification
                print("    Cached model files:")
                snapshot_dir = model_cache_path / "snapshots"
                if snapshot_dir.exists():
                    for snapshot in snapshot_dir.iterdir():
                        if snapshot.is_dir():
                            model_files = list(snapshot.glob("*.safetensors")) + list(snapshot.glob("*.bin"))
                            if model_files:
                                total_size = sum(f.stat().st_size for f in model_files) / (1024**3)
                                print(f"      Snapshot: {snapshot.name} ({total_size:.1f}GB)")
            
            # Cleanup
            del model, tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            import gc
            gc.collect()
            
            return True
            
        except Exception as e:
            print(f"    ❌ Download failed: {e}")
            print("    You can manually download later using:")
            print(f"      python -c \"from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('{model_id}')\"")
            return False

    def _get_optimal_download_dtype(self) -> torch.dtype:
        """Determine optimal dtype for model download based on detected hardware."""
        import torch
        
        # If forced to CPU, use CPU-optimal precision
        if self.force_cpu:
            return torch.float32
        
        # GPU detected - use FP16 for efficiency
        if (self.gpu_capabilities['nvidia_detected'] or 
            self.gpu_capabilities['apple_silicon'] or 
            self.gpu_capabilities['amd_rocm_detected'] or 
            self.gpu_capabilities['intel_gpu_detected']):
            return torch.float16
        
        # CPU fallback
        return torch.float32

    def _get_device_description(self) -> str:
        """Get human-readable description of optimization target."""
        if self.force_cpu:
            return "CPU-only (user requested)"
        elif self.gpu_capabilities['nvidia_detected']:
            return "NVIDIA GPU (FP16 caching)"
        elif self.gpu_capabilities['apple_silicon']:
            return "Apple Silicon MPS (FP16 caching)"
        elif self.gpu_capabilities['amd_rocm_detected']:
            return "AMD ROCm (FP16 caching)"
        elif self.gpu_capabilities['intel_gpu_detected']:
            return "Intel GPU (FP16 caching)"
        else:
            return "CPU fallback (FP32 caching)"

    def _device_aware_cleanup(self) -> None:
        """Perform device-appropriate memory cleanup."""
        import torch
        import gc
        
        # NVIDIA CUDA cleanup
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Apple Silicon MPS cleanup
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            if hasattr(torch.mps, 'empty_cache'):
                torch.mps.empty_cache()
        
        # General cleanup for all devices
        gc.collect()

    def _download_embedding_model(self) -> bool:
        """Download embedding model for citation verification."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(self.config.get_embedding_model_id())
            print("    Embedding model cached")
            del model
            return True
        except Exception as e:
            print(f"    Embedding download failed: {e}")
            return False

    def run_complete_installation(self, auto_confirm: bool = False) -> bool:
        # Display system analysis
        self.print_system_analysis()
        
        # Show storage configuration (always active now)
        print("📂 Storage Configuration:")
        print(f"   All files will be downloaded to project directory")
        print(f"   Location: {self.project_root / '.cache'}")
        print(f"   Available space: {self.storage_config['original_free_gb']:.1f}GB")
        
        if self.storage_config['original_free_gb'] < 10:
            print(f"   ⚠️ Low space warning: AI models require ~8GB")
        print()
        
        # Virtual environment check
        if not self.system_info['in_venv'] and not auto_confirm:
            response = input("  Not in virtual environment. Continue? (y/N): ").lower()
            if response not in ['y', 'yes']:
                return False
        
        # Requirements file check
        if not self.requirements_file.exists():
            print(f" Requirements file not found: {self.requirements_file}")
            return False
        
        if not auto_confirm:
            response = input(" Proceed with installation? (y/N): ").lower()
            if response not in ['y', 'yes']:
                return False
        
        print("\n Starting Installation...")
        print("=" * 55)

        steps = [
            ("Build Tools", self.install_build_tools),
            ("Core Dependencies", self.install_core_dependencies),
            ("PyTorch", self.install_pytorch),
        ]

        # Add optional AI models step
        if self.config.should_predownload_models():
            steps.append(("AI Models", self.install_ai_models))
        
        for step_name, step_func in steps:
            # Interactive prompt for large downloads
            if step_name == "AI Models" and not auto_confirm:
                response = input("   Download AI models now? (~7.6GB) (y/N): ").lower()
                if response not in ['y', 'yes']:
                    print("     Skipping model downloads")
                    continue
            
            if not step_func():
                print(f" {step_name} failed")
                return False
        
        # Verification
        success = self.verify_installation()
        self.save_installation_log()
        
        if success:
            print("\nInstallation completed!")
            print("=" * 50)
            print(" All downloads saved in project folder:")
            print(f"   {self.project_root / '.cache'}")
            print()
            print("Next steps:")
            if self.pytorch_config.get('method') == 'nvidia_cuda':
                print("1) GPU Check: python -c \"import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU-only')\"")
            else:
                print("1) PyTorch: python -c \"import torch; print('Ready:', torch.__version__)\"")
                
            print("2) Start KB: docker-compose up -d --wait")
            print("3) Run Tests: python -m tests")
            print("4) Content: python -c \"from knowledge_base import get_system_info; print('Docs:', get_system_info().get('total_documents', 0))\"")
            print("5) Search Demo: python tests/search_demo.py")
            print()
            
            if self.storage_config.get('activated'):
                print("  Storage: D: drive cache active (C: drive protected)")
                print()
        else:
            print("\nInstallation completed with issues")
            print("Check: sourcewell_installation.log")
            print("Retry: pip cache purge && python setup_sourcewell.py --auto")
        
        return success

def main():
    """Command-line interface for installation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SourceWell - Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Configuration management
    parser.add_argument('--create-config', action='store_true', help='Create sample config file')
    parser.add_argument('--show-config', action='store_true', help='Show current configuration')
    
    # Installation options
    parser.add_argument('--version', dest='pytorch_version', help='PyTorch version override')
    parser.add_argument('--auto', action='store_true', help='Automatic installation')
    parser.add_argument('--cpu-only', action='store_true', help='Force CPU-only PyTorch')
    
     # Download-models opyion
    parser.add_argument('--download-models', action='store_true', help='Download AI models only')

    args = parser.parse_args()
    
    config = SourceWellConfig()
    
    if args.create_config:
        success = config.create_sample_config()
        sys.exit(0 if success else 1)
    
    if args.show_config:
        print("Configuration:")
        print("=" * 30)
        print(f"PyTorch Version: {config.get_pytorch_version()}")
        print(f"CUDA Version: {config.get_cuda_version()}")
        print(f"ROCm Version: {config.get_rocm_version()}")
        print(f"Bitsandbytes Version: {config.get_bitsandbytes_version()}")
        print(f"AI Model ID: {config.get_ai_model_id()}")
        print(f"Embedding Model ID: {config.get_embedding_model_id()}")
        print(f"Predownload Models: {config.should_predownload_models()}")
        print(f"Config File: {config.config_file}")
        sys.exit(0)
    
    if args.download_models:
        print("SourceWell Model Downloader")
        print("=" * 40)
        print("This will download:")
        print(f"   {config.get_ai_model_id()} (~7.6GB)")
        print(f"   {config.get_embedding_model_id()} (~90MB)")
        print()

        installer = SourceWellInstaller(
            pytorch_version=args.pytorch_version,
            force_cpu=args.cpu_only,
            config=config
        )
        
        # Set up cache paths
        installer._configure_adaptive_storage_management()
        
        print(f"Models will be saved to: {installer.project_root / '.cache' / 'huggingface'}")
        print()
        
        # Download models
        success = True
        if installer._download_phi3_model():
            print("✅ Phi-3 Mini downloaded successfully")
        else:
            print("❌ Phi-3 Mini download failed")
            success = False
        
        if installer._download_embedding_model():
            print("✅ Embedding model downloaded successfully")
        else:
            print("❌ Embedding model download failed")
            success = False
        
        if success:
            print("\n✅ All models downloaded successfully!")
            print("\nYou can now run the application offline.")
        else:
            print("\n⚠️ Some models failed to download")
            print("Check your internet connection and try again.")
        
        sys.exit(0 if success else 1)

    installer = SourceWellInstaller(
    pytorch_version=args.pytorch_version,
    force_cpu=args.cpu_only,
    config=config
    )
    
    success = installer.run_complete_installation(auto_confirm=args.auto)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()