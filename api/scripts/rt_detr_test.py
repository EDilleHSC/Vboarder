"""
Unit Test Suite for RT-DETR v2 Model Pipeline
Validates model loading, inference, and performance
Run weekly via CI/CD or cron job
"""

import unittest
import torch
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor
from PIL import Image
import numpy as np
import time
from pathlib import Path
import json
from datetime import datetime


class TestRTDetrV2Pipeline(unittest.TestCase):
    """Test suite for RT-DETR v2 object detection pipeline"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests"""
        print("\n" + "="*60)
        print("🧪 RT-DETR v2 Pipeline Test Suite")
        print("="*60)
        
        cls.model_name = "PekingU/rtdetr_r50vd_coco_o365"
        cls.test_results = {
            "timestamp": datetime.now().isoformat(),
            "model": cls.model_name,
            "tests": []
        }
        
        # Create a simple test image
        cls.test_image = Image.new('RGB', (640, 480), color='red')
        
    def test_01_cuda_available(self):
        """Test 1: Verify CUDA is available"""
        print("\n🔍 Test 1: CUDA Availability")
        
        cuda_available = torch.cuda.is_available()
        
        result = {
            "test": "cuda_available",
            "passed": cuda_available,
            "details": {
                "cuda_available": cuda_available,
                "device_name": torch.cuda.get_device_name(0) if cuda_available else None,
                "cuda_version": torch.version.cuda
            }
        }
        
        self.test_results["tests"].append(result)
        
        if cuda_available:
            print(f"  ✅ CUDA Available: {torch.cuda.get_device_name(0)}")
        else:
            print(f"  ⚠️ CUDA Not Available - tests will run on CPU")
        
        self.assertTrue(cuda_available, "CUDA should be available for GPU-accelerated inference")
    
    def test_02_model_loading(self):
        """Test 2: Verify RT-DETR v2 model loads successfully"""
        print("\n🔍 Test 2: Model Loading")
        
        try:
            start_time = time.time()
            
            # Load processor
            processor = RTDetrImageProcessor.from_pretrained(self.model_name)
            
            # Load model
            model = RTDetrForObjectDetection.from_pretrained(self.model_name)
            
            if torch.cuda.is_available():
                model = model.to('cuda')
            
            load_time = time.time() - start_time
            
            result = {
                "test": "model_loading",
                "passed": True,
                "details": {
                    "model_name": self.model_name,
                    "load_time_seconds": round(load_time, 2),
                    "device": "cuda" if torch.cuda.is_available() else "cpu",
                    "model_params": sum(p.numel() for p in model.parameters()),
                }
            }
            
            self.test_results["tests"].append(result)
            
            print(f"  ✅ Model loaded successfully")
            print(f"  ⏱️ Load time: {load_time:.2f}s")
            print(f"  📊 Parameters: {result['details']['model_params']:,}")
            
            # Store for next tests
            self.__class__.processor = processor
            self.__class__.model = model
            
        except Exception as e:
            result = {
                "test": "model_loading",
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests"].append(result)
            
            print(f"  ❌ Failed to load model: {e}")
            self.fail(f"Model loading failed: {e}")
    
    def test_03_inference(self):
        """Test 3: Verify model can perform inference"""
        print("\n🔍 Test 3: Inference Test")
        
        try:
            # Prepare inputs
            inputs = self.processor(images=self.test_image, return_tensors="pt")
            
            if torch.cuda.is_available():
                inputs = {k: v.to('cuda') for k, v in inputs.items()}
            
            # Run inference
            start_time = time.time()
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            inference_time = time.time() - start_time
            
            # Check outputs
            has_logits = hasattr(outputs, 'logits')
            has_boxes = hasattr(outputs, 'pred_boxes')
            
            result = {
                "test": "inference",
                "passed": has_logits and has_boxes,
                "details": {
                    "inference_time_seconds": round(inference_time, 3),
                    "output_shape": str(outputs.logits.shape) if has_logits else None,
                    "has_logits": has_logits,
                    "has_boxes": has_boxes,
                }
            }
            
            self.test_results["tests"].append(result)
            
            print(f"  ✅ Inference successful")
            print(f"  ⏱️ Inference time: {inference_time:.3f}s")
            
            self.assertTrue(has_logits, "Output should contain logits")
            self.assertTrue(has_boxes, "Output should contain bounding boxes")
            
        except Exception as e:
            result = {
                "test": "inference",
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests"].append(result)
            
            print(f"  ❌ Inference failed: {e}")
            self.fail(f"Inference failed: {e}")
    
    def test_04_performance_benchmark(self):
        """Test 4: Benchmark inference performance"""
        print("\n🔍 Test 4: Performance Benchmark")
        
        num_runs = 10
        inference_times = []
        
        try:
            inputs = self.processor(images=self.test_image, return_tensors="pt")
            
            if torch.cuda.is_available():
                inputs = {k: v.to('cuda') for k, v in inputs.items()}
            
            # Warm-up run
            with torch.no_grad():
                _ = self.model(**inputs)
            
            # Benchmark runs
            for i in range(num_runs):
                start_time = time.time()
                
                with torch.no_grad():
                    _ = self.model(**inputs)
                
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                
                inference_times.append(time.time() - start_time)
            
            avg_time = np.mean(inference_times)
            std_time = np.std(inference_times)
            
            # Performance threshold: should be under 0.5s on GPU
            threshold = 0.5 if torch.cuda.is_available() else 2.0
            passes_threshold = avg_time < threshold
            
            result = {
                "test": "performance_benchmark",
                "passed": passes_threshold,
                "details": {
                    "num_runs": num_runs,
                    "avg_inference_time": round(avg_time, 3),
                    "std_dev": round(std_time, 3),
                    "min_time": round(min(inference_times), 3),
                    "max_time": round(max(inference_times), 3),
                    "threshold_seconds": threshold,
                    "passes_threshold": passes_threshold,
                }
            }
            
            self.test_results["tests"].append(result)
            
            status = "✅" if passes_threshold else "⚠️"
            print(f"  {status} Avg inference: {avg_time:.3f}s (±{std_time:.3f}s)")
            print(f"  📊 Min/Max: {min(inference_times):.3f}s / {max(inference_times):.3f}s")
            print(f"  🎯 Threshold: {threshold}s")
            
            if not passes_threshold:
                print(f"  ⚠️ WARNING: Performance below threshold")
            
        except Exception as e:
            result = {
                "test": "performance_benchmark",
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests"].append(result)
            print(f"  ❌ Benchmark failed: {e}")
    
    def test_05_memory_usage(self):
        """Test 5: Check GPU memory usage"""
        print("\n🔍 Test 5: Memory Usage Check")
        
        if not torch.cuda.is_available():
            print("  ⚠️ Skipping - CUDA not available")
            return
        
        try:
            torch.cuda.reset_peak_memory_stats()
            
            inputs = self.processor(images=self.test_image, return_tensors="pt")
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
            
            with torch.no_grad():
                _ = self.model(**inputs)
            
            peak_memory = torch.cuda.max_memory_allocated() / 1e6  # MB
            current_memory = torch.cuda.memory_allocated() / 1e6
            
            # Memory threshold: should use less than 4GB
            threshold_mb = 4000
            passes_threshold = peak_memory < threshold_mb
            
            result = {
                "test": "memory_usage",
                "passed": passes_threshold,
                "details": {
                    "peak_memory_mb": round(peak_memory, 2),
                    "current_memory_mb": round(current_memory, 2),
                    "threshold_mb": threshold_mb,
                    "passes_threshold": passes_threshold,
                }
            }
            
            self.test_results["tests"].append(result)
            
            status = "✅" if passes_threshold else "⚠️"
            print(f"  {status} Peak memory: {peak_memory:.2f} MB")
            print(f"  📊 Current memory: {current_memory:.2f} MB")
            print(f"  🎯 Threshold: {threshold_mb} MB")
            
        except Exception as e:
            result = {
                "test": "memory_usage",
                "passed": False,
                "error": str(e)
            }
            self.test_results["tests"].append(result)
            print(f"  ❌ Memory check failed: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Generate final report and save results"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(cls.test_results["tests"])
        passed_tests = sum(1 for t in cls.test_results["tests"] if t["passed"])
        
        cls.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0
        }
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {total_tests - passed_tests} ❌")
        print(f"Pass Rate: {cls.test_results['summary']['pass_rate']*100:.1f}%")
        
        # Convert numpy/torch types to native Python types for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(v) for v in obj]
            elif hasattr(obj, 'item'):  # numpy/torch scalar
                return obj.item()
            elif isinstance(obj, (bool, int, float, str, type(None))):
                return obj
            else:
                return str(obj)
        
        # Save results to JSON
        results_file = Path(f"rt_detr_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump(convert_to_serializable(cls.test_results), f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Shift report format
        print("\n" + "="*60)
        print("📋 SHIFT REPORT ENTRY")
        print("="*60)
        
        status = "✅" if passed_tests == total_tests else "⚠️"
        print(f"\nRT-DETR v2 Pipeline Test: {status}")
        print(f"  Pass Rate: {cls.test_results['summary']['pass_rate']*100:.1f}%")
        
        for test in cls.test_results["tests"]:
            status = "✅" if test["passed"] else "❌"
            print(f"  {status} {test['test']}")


def run_weekly_test():
    """Helper function to run as a weekly cron job"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRTDetrV2Pipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code for CI/CD
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)