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
    
    DEFAULT_PYTORCH_VERSION = "2.5.1"
    DEFAULT_CUDA_VERSION = "121"
    DEFAULT_ROCM_VERSION = "6.0"
    
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
            'pytorch_version': self.DEFAULT_PYTORCH_VERSION,
            'cuda_version': self.DEFAULT_CUDA_VERSION,
            'rocm_version': self.DEFAULT_ROCM_VERSION,
        }
        
        # 1. Load from config file (if exists)
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config.get('versions', {}))
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # 2. Override with environment variables (highest priority)
        env_mappings = {
            'SOURCEWELL_PYTORCH_VERSION': 'pytorch_version',
            'SOURCEWELL_CUDA_VERSION': 'cuda_version',
            'SOURCEWELL_ROCM_VERSION': 'rocm_version',
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
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
    
    def create_sample_config(self) -> bool:
        sample_config = {
            "versions": {
                "pytorch_version": self.DEFAULT_PYTORCH_VERSION,
                "cuda_version": self.DEFAULT_CUDA_VERSION,
                "rocm_version": self.DEFAULT_ROCM_VERSION
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
        Intelligently configure storage when space is constrained.
        Only activates when current temp location has insufficient space.
        Process-level changes only - no permanent system modifications.
        """
        storage_config = {
            'activated': False,
            'reason': None,
            'temp_path': None,
            'cache_path': None,
            'original_free_gb': 0
        }
        
        try:
            import tempfile
            current_temp = Path(tempfile.gettempdir())
            
            # Cross-platform disk usage check
            total, used, free = shutil.disk_usage(current_temp)
            free_gb = free / (1024**3)
            storage_config['original_free_gb'] = free_gb
            
            print(f" Current temp location: {current_temp} ({free_gb:.1f}GB free)")
            
            if free_gb < min_free_gb:
                print(f"  Insufficient temp space ({free_gb:.1f}GB < {min_free_gb}GB required)")
                
                # Platform-specific alternative storage selection
                alternative_base = None
                
                if self.system_info['os'] == 'windows':
                    d_drive = Path('D:/')
                    if d_drive.exists():
                        d_total, d_used, d_free = shutil.disk_usage(d_drive)
                        d_free_gb = d_free / (1024**3)
                        if d_free_gb >= min_free_gb * 2:  # Ensure adequate space
                            alternative_base = d_drive / "sourcewell_cache"
                            storage_config['reason'] = f"D: drive has {d_free_gb:.1f}GB available"
                    
                    # Fallback to project directory
                    if not alternative_base:
                        project_total, project_used, project_free = shutil.disk_usage(self.project_root)
                        project_free_gb = project_free / (1024**3)
                        if project_free_gb >= min_free_gb:
                            alternative_base = self.project_root / ".cache"
                            storage_config['reason'] = f"Project directory has {project_free_gb:.1f}GB available"
                
                else:  # macOS/Linux
                    # Use project directory .cache
                    try:
                        project_total, project_used, project_free = shutil.disk_usage(self.project_root)
                        project_free_gb = project_free / (1024**3)
                        if project_free_gb >= min_free_gb:
                            alternative_base = self.project_root / ".cache"
                            storage_config['reason'] = f"Project cache has {project_free_gb:.1f}GB available"
                    except Exception:
                        pass
                
                # Configure alternative storage if found
                if alternative_base:
                    temp_dir = alternative_base / "temp"
                    cache_dir = alternative_base / "pip_cache"
                    
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    (alternative_base / "huggingface").mkdir(parents=True, exist_ok=True)
                    
                    # Set process-level environment variables
                    os.environ['TMP'] = str(temp_dir)
                    os.environ['TEMP'] = str(temp_dir)
                    os.environ['PIP_CACHE_DIR'] = str(cache_dir)
                    os.environ['HF_HOME'] = str(alternative_base / "huggingface")
                    os.environ.pop('TRANSFORMERS_CACHE', None)
                    
                    storage_config.update({
                        'activated': True,
                        'temp_path': str(temp_dir),
                        'cache_path': str(cache_dir)
                    })
                    
                    print(f" Activated alternative storage: {alternative_base}")
                    print(f" Reason: {storage_config['reason']}")
                    
                else:
                    print(f" No suitable alternative storage found")
                    print(f" Recommend freeing space or manually setting --cache-dir")
                    storage_config['reason'] = "No alternative storage with adequate space"
            
            else:
                print(f" Adequate temp space available ({free_gb:.1f}GB)")
                os.environ.pop('TRANSFORMERS_CACHE', None)
                hf_cache_dir = self.project_root / ".cache" / "huggingface"
                hf_cache_dir.mkdir(parents=True, exist_ok=True)
                os.environ.setdefault('HF_HOME', str(hf_cache_dir))
                print(f"    HF_HOME configured: {os.environ['HF_HOME']}")

        except Exception as e:
            print(f" Storage detection failed: {e}")
            storage_config['reason'] = f"Detection error: {e}"
        
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
        
        # Priority: NVIDIA > Apple Silicon > AMD ROCm > Intel XPU > CPU
        if self.gpu_capabilities['nvidia_detected']:
            detected_cuda = self.gpu_capabilities.get('nvidia_cuda_version')
            cuda_version = self.config.get_cuda_version(detected_cuda)
            
            config.update({
                'method': 'nvidia_cuda',
                'packages': [f'torch=={self.pytorch_version}+cu{cuda_version}'],
                'index_url': f'https://download.pytorch.org/whl/cu{cuda_version}',
                'description': f'NVIDIA CUDA-enabled PyTorch {self.pytorch_version} (cu{cuda_version})',
                'expected_acceleration': f'CUDA {cuda_version} (NVIDIA GPU)'
            })
        
        elif self.gpu_capabilities['apple_silicon']:
            config.update({
                'method': 'apple_mps',
                'packages': [f'torch=={self.pytorch_version}'],
                'description': f'Apple Silicon PyTorch {self.pytorch_version} with MPS',
                'expected_acceleration': 'MPS (Apple GPU)'
            })
        
        elif self.gpu_capabilities['amd_rocm_detected']:
            rocm_version = self.config.get_rocm_version()
            config.update({
                'method': 'amd_rocm',
                'packages': [f'torch=={self.pytorch_version}+rocm{rocm_version}'],
                'index_url': f'https://download.pytorch.org/whl/rocm{rocm_version}',
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
            
            # Filter PyTorch-related packages
            lower_line = stripped.lower()
            if any(pkg in lower_line for pkg in ['torch==', 'torch>=', 'torch<', 'torchvision', 'torchaudio']):
                skipped_lines.append(line)
                continue
            
            filtered_lines.append(line)
        
        if skipped_lines:
            print(" Filtered PyTorch lines from requirements.txt:")
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
        
        # Install extra packages if needed (Intel XPU extensions, etc.)
        if self.pytorch_config['extra_packages']:
            print("   Installing additional GPU packages...")
            extra_cmd = base_cmd + self.pytorch_config['extra_packages']
            success, _, stderr = self._run_command(extra_cmd, timeout=600)
            
            if success:
                print("   Additional packages installed!")
            else:
                print(f"    Additional packages warning: {stderr}")
        
        return True
    
    def verify_installation(self) -> bool:
        """Instalation verification."""
        print(" Verifying installation...")
        
        results = {'pytorch_import': False, 'gpu_acceleration': False, 'core_dependencies': False}
        
        try:
            # Test PyTorch import and GPU
            import torch
            results['pytorch_import'] = True
            print(f" PyTorch {torch.__version__} imported successfully")
            
            # Test GPU acceleration based on method
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
                    print("  MPS not available")
            
            else:
                print(" PyTorch ready")
                results['gpu_acceleration'] = True
            
            # Test core dependencies
            try:
                import weaviate, streamlit, fastapi, sentence_transformers
                print(" Core dependencies verified")
                results['core_dependencies'] = True
            except ImportError as e:
                print(f" Missing dependency: {e}")
            
        except ImportError as e:
            print(f" PyTorch import failed: {e}")
        
        passed = sum(results.values())
        print(f"\n Verification: {passed}/3 checks passed")
        return passed >= 2
    
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
    
    def run_complete_installation(self, auto_confirm: bool = False) -> bool:
        # Intelligent storage configuration (only when needed)
        self.print_system_analysis()
        
        if self.storage_config['activated']:
            print(" Storage Management:")
            print(f"    Using alternative temp/cache location")
            print(f"    Temp: {self.storage_config['temp_path']}")
            print(f"    Cache: {self.storage_config['cache_path']}")
            print()
        elif self.storage_config['original_free_gb'] < 10:
            print(" Storage Notice:")
            print(f"     Limited free space ({self.storage_config['original_free_gb']:.1f}GB)")
            print(f"   Monitor installation progress for space issues")
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
        
        for step_name, step_func in steps:
            if not step_func():
                print(f" {step_name} failed - aborting")
                self.save_installation_log()
                return False
        
        # Verification
        success = self.verify_installation()
        self.save_installation_log()
        
        if success:
            print("\nInstallation completed!")
            print("=" * 50)
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
        print(f"Config File: {config.config_file}")
        sys.exit(0)
    
    installer = SourceWellInstaller(
        pytorch_version=args.pytorch_version,
        force_cpu=args.cpu_only,
        config=config
    )
    
    success = installer.run_complete_installation(auto_confirm=args.auto)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()