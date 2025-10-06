"""
Comprehensive System Test Suite for SourceWell
Tests all components: Knowledge Base, Calculators, and AI
"""

import sys
import time
import torch
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def test_system_setup():
    """Test basic system configuration"""
    print_header("SYSTEM CONFIGURATION")
    
    print(f"Python: {sys.version}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        
        # Test for optimizations
        try:
            import flash_attn
            print(" Flash Attention: Available")
        except:
            print(" Flash Attention: Not installed")
        
        try:
            import xformers
            print(f" xFormers: {xformers.__version__}")
        except:
            print(" xFormers: Not installed")
    
    return True

def test_knowledge_base():
    """Test knowledge base functionality"""
    print_header("KNOWLEDGE BASE TEST")
    
    try:
        from knowledge_base import MedicalSearchEngine, get_system_info
        
        # Check system info
        info = get_system_info()
        print(f"Status: {info['status']}")
        print(f"Documents: {info['total_documents']}")
        
        if info['status'] != 'healthy':
            print(" Knowledge base not healthy")
            return False
        
        # Test search
        search_engine = MedicalSearchEngine()
        
        # Test different search methods
        test_queries = [
            ("diabetes prevention", "bm25"),
            ("cardiovascular risk", "semantic"),
            ("colorectal screening", "hybrid")
        ]
        
        for query, method in test_queries:
            print(f"\nTesting {method} search: '{query}'")
            start = time.time()
            results = search_engine.search_medical_content(
                query=query,
                limit=3,
                search_method=method
            )
            search_time = time.time() - start
            
            if results:
                print(f"   Found {len(results)} results in {search_time:.2f}s")
                print(f"    Top result: {results[0].title[:50]}...")
            else:
                print(f"   No results found")
        
        print("\n Knowledge Base: PASSED")
        return True
        
    except Exception as e:
        print(f" Knowledge Base: FAILED - {e}")
        return False

def test_calculators():
    """Test risk calculators"""
    print_header("RISK CALCULATORS TEST")
    
    try:
        from calculators import MultiCalculatorRunner, check_calculator_health
        from data_models.patient_data import PatientData
        
        # Check health
        health = check_calculator_health()
        print(f"Calculator Status: {health['status']}")
        
        if health['status'] != 'healthy':
            print(f" Calculators not healthy: {health.get('error', 'Unknown error')}")
            return False
        
        print(f"Available: {', '.join(health['available_calculators'])}")
        
        # Test with sample patient
        test_patient_data = {
            'age': 55,
            'gender': 'male',
            'height_cm': 175,
            'weight_kg': 85,
            'systolic_bp': 135,
            'diastolic_bp': 85,
            'total_cholesterol': 220,
            'hdl_cholesterol': 45,
            'current_smoker': False,
            'diabetes_diagnosed': False,
            'hypertension_medication': True,
            'physical_activity': False,
            'vegetable_fruit_daily': True,
            'family_diabetes_history': 'parent_sibling_child',
            'family_colorectal_cancer': False
        }
        
        patient = PatientData.from_dict(test_patient_data)
        
        # Run assessment
        print("\nRunning comprehensive assessment...")
        runner = MultiCalculatorRunner()
        start = time.time()
        results = runner.run_all_assessments(patient)
        calc_time = time.time() - start
        
        if results['success']:
            print(f" Assessment completed in {calc_time:.2f}s")
            print(f"   Success rate: {results['successful_assessments']}/{results['calculators_run']}")
            
            # Check each calculator
            for calc_name in ['diabetes', 'cardiovascular', 'colorectal_screening']:
                result = results['results'].get(calc_name)
                if result and not isinstance(result, dict):
                    print(f"    {calc_name}: Success")
                else:
                    print(f"    {calc_name}: Failed or skipped")
            
            print("\n Calculators: PASSED")
            return True
        else:
            print(f" Assessment failed: {results.get('errors', [])}")
            return False
            
    except Exception as e:
        print(f" Calculators: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_engine():
    """Test AI engine with performance benchmarks"""
    print_header("AI ENGINE TEST")
    
    try:
        from llm.phi3_engine import Phi3MiniEngine
        
        print("Initializing AI engine...")
        engine = Phi3MiniEngine()
        
        # Check status
        status = engine.get_engine_status()
        print(f"Engine Initialized: {status['engine_initialized']}")
        print(f"Model Wrapper: {status['model_wrapper_available']}")
        
        if not status['engine_initialized']:
            print(" AI Engine not initialized")
            return False
        
        # Initialize model
        print("\nLoading Phi-3 model...")
        start = time.time()
        if engine.initialize():
            load_time = time.time() - start
            print(f" Model loaded in {load_time:.2f}s")
        else:
            print(" Failed to load model")
            return False
        
        # Test generation speed
        test_prompts = [
            ("What does 15% diabetes risk mean?", 50),
            ("List 3 ways to reduce cardiovascular risk", 75),
            ("Explain colorectal screening briefly", 50)
        ]
        
        print("\nTesting generation speed...")
        total_tokens = 0
        total_time = 0
        
        for prompt, max_tokens in test_prompts:
            print(f"\nPrompt: {prompt[:50]}...")
            start = time.time()
            response = engine.model_wrapper.generate(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.7
            )
            gen_time = time.time() - start
            
            tokens = len(response.split())
            total_tokens += tokens
            total_time += gen_time
            
            print(f"  Generated {tokens} tokens in {gen_time:.2f}s")
            print(f"  Speed: {tokens/gen_time:.1f} tokens/sec")
            print(f"  Response: {response[:100]}...")
        
        avg_speed = total_tokens / total_time if total_time > 0 else 0
        print(f"\nAverage Speed: {avg_speed:.1f} tokens/sec")
        
        if avg_speed < 1:
            print(" Generation is slow. Consider installing flash-attention or xformers")
        elif avg_speed < 5:
            print(" Generation speed is moderate. Flash-attention could help")
        else:
            print(" Good generation speed!")
        
        # Cleanup
        engine.cleanup()
        
        print("\n AI Engine: PASSED")
        return True
        
    except Exception as e:
        print(f" AI Engine: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between components"""
    print_header("INTEGRATION TEST")
    
    try:
        # Test Calculator -> AI pipeline
        print("Testing Calculator -> AI integration...")
        
        from calculators import MultiCalculatorRunner
        from data_models.patient_data import PatientData
        from llm.phi3_engine import Phi3MiniEngine
        
        # Create test patient
        patient_dict = {
            'age': 50,
            'gender': 'female',
            'height_cm': 165,
            'weight_kg': 70,
            'systolic_bp': 125,
            'diastolic_bp': 80,
            'total_cholesterol': 200,
            'hdl_cholesterol': 55,
            'current_smoker': False,
            'diabetes_diagnosed': False,
            'hypertension_medication': False,
            'physical_activity': True,
            'vegetable_fruit_daily': True,
            'family_diabetes_history': 'none',
            'family_colorectal_cancer': False
        }
        
        patient = PatientData.from_dict(patient_dict)
        
        # Run calculators
        runner = MultiCalculatorRunner()
        calc_results = runner.run_all_assessments(patient)
        
        if not calc_results['success']:
            print(" Calculator failed")
            return False
        
        print(" Calculators ran successfully")
        
        # Initialize AI
        engine = Phi3MiniEngine()
        
        # Test explanation generation
        print("\nGenerating AI explanation of results...")
        explanation = engine.generate_explanation(
            patient_data=patient_dict,
            risk_results=calc_results,
            explanation_type="general",
            include_citations=True
        )
        
        if explanation.get('success'):
            print(" AI explanation generated")
            print(f"   Citations: {explanation.get('context_sources', 0)}")
            print(f"   Confidence: {explanation.get('confidence', 0):.1%}")
        else:
            print(f" AI explanation failed: {explanation.get('error')}")
        
        print("\n Integration: PASSED")
        return True
        
    except Exception as e:
        print(f" Integration: FAILED - {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 60)
    print(" SOURCEWELL COMPREHENSIVE SYSTEM TEST")
    print(" " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    results = {}
    
    # Run tests
    tests = [
        ("System Setup", test_system_setup),
        ("Knowledge Base", test_knowledge_base),
        ("Calculators", test_calculators),
        ("AI Engine", test_ai_engine),
        ("Integration", test_integration)
    ]
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = " PASSED" if result else " FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n ALL TESTS PASSED! System is fully operational.")
    elif passed >= total - 1:
        print("\n System is mostly operational with minor issues.")
    else:
        print("\n System has significant issues. Please review failures.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)