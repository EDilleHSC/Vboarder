"""
GPU Memory Monitor for Production Workloads
Tracks memory usage, temperature, and utilization
"""

import torch
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import subprocess


class GPUMonitor:
    def __init__(self, log_file: str = "gpu_monitor.jsonl"):
        self.log_file = Path(log_file)
        self.baseline_memory = 0
        self.peak_memory = 0
        self.samples = []
        
    def check_availability(self) -> Dict:
        """Check if GPU is available and get basic info"""
        if not torch.cuda.is_available():
            return {"available": False, "error": "CUDA not available"}
        
        return {
            "available": True,
            "device_name": torch.cuda.get_device_name(0),
            "device_count": torch.cuda.device_count(),
            "cuda_version": torch.version.cuda,
            "pytorch_version": torch.__version__,
        }
    
    def get_memory_stats(self) -> Dict:
        """Get current memory statistics"""
        if not torch.cuda.is_available():
            return {}
        
        allocated = torch.cuda.memory_allocated(0) / 1e6  # MB
        reserved = torch.cuda.memory_reserved(0) / 1e6
        max_allocated = torch.cuda.max_memory_allocated(0) / 1e6
        total = torch.cuda.get_device_properties(0).total_memory / 1e6
        
        return {
            "allocated_mb": round(allocated, 2),
            "reserved_mb": round(reserved, 2),
            "max_allocated_mb": round(max_allocated, 2),
            "total_mb": round(total, 2),
            "utilization_pct": round((allocated / total) * 100, 2),
        }
    
    def get_temperature(self) -> float:
        """Get GPU temperature using nvidia-smi"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return float(result.stdout.strip())
        except Exception:
            return None
    
    def start_monitoring(self):
        """Set baseline and reset peak stats"""
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            self.baseline_memory = torch.cuda.memory_allocated(0) / 1e6
            print(f"🎮 GPU Monitoring Started")
            print(f"  Baseline Memory: {self.baseline_memory:.2f} MB")
    
    def sample(self) -> Dict:
        """Take a single measurement sample"""
        sample = {
            "timestamp": datetime.now().isoformat(),
            "memory": self.get_memory_stats(),
            "temperature_c": self.get_temperature(),
        }
        
        self.samples.append(sample)
        return sample
    
    def monitor_workload(self, duration_seconds: int = 60, interval_seconds: int = 1):
        """Monitor GPU during a workload"""
        print(f"📊 Monitoring GPU for {duration_seconds}s (interval: {interval_seconds}s)")
        
        self.start_monitoring()
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            sample = self.sample()
            
            # Print summary
            mem = sample['memory']
            temp = sample['temperature_c']
            print(f"  [{int(time.time() - start_time)}s] "
                  f"Memory: {mem['allocated_mb']:.1f}MB "
                  f"({mem['utilization_pct']:.1f}%) "
                  f"Temp: {temp}°C" if temp else "")
            
            time.sleep(interval_seconds)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate monitoring report"""
        if not self.samples:
            return {"error": "No samples collected"}
        
        # Calculate statistics
        mem_samples = [s['memory']['allocated_mb'] for s in self.samples]
        temp_samples = [s['temperature_c'] for s in self.samples if s['temperature_c']]
        
        report = {
            "duration_seconds": len(self.samples),
            "samples_collected": len(self.samples),
            "memory": {
                "baseline_mb": self.baseline_memory,
                "min_mb": min(mem_samples),
                "max_mb": max(mem_samples),
                "avg_mb": sum(mem_samples) / len(mem_samples),
                "peak_delta_mb": max(mem_samples) - self.baseline_memory,
            },
            "temperature": {
                "min_c": min(temp_samples) if temp_samples else None,
                "max_c": max(temp_samples) if temp_samples else None,
                "avg_c": sum(temp_samples) / len(temp_samples) if temp_samples else None,
            }
        }
        
        return report
    
    def print_report(self):
        """Print formatted report for shift handoff"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("🎮 GPU MONITORING REPORT")
        print("="*60)
        
        mem = report['memory']
        print(f"\n📊 Memory Usage:")
        print(f"  Baseline: {mem['baseline_mb']:.2f} MB")
        print(f"  Peak: {mem['max_mb']:.2f} MB")
        print(f"  Average: {mem['avg_mb']:.2f} MB")
        print(f"  Peak Delta: {mem['peak_delta_mb']:.2f} MB")
        
        if report['temperature']['avg_c']:
            temp = report['temperature']
            print(f"\n🌡️ Temperature:")
            print(f"  Min: {temp['min_c']:.1f}°C")
            print(f"  Max: {temp['max_c']:.1f}°C")
            print(f"  Average: {temp['avg_c']:.1f}°C")
            
            # Warning thresholds
            if temp['max_c'] > 80:
                print("  ⚠️ WARNING: Peak temperature exceeded 80°C")
            elif temp['max_c'] > 70:
                print("  ⚠️ Caution: Peak temperature above 70°C")
        
        print(f"\n📈 Monitoring Duration: {report['duration_seconds']}s")
        print(f"📊 Samples Collected: {report['samples_collected']}")
        
        return report
    
    def save_log(self):
        """Save samples to JSONL log file"""
        with open(self.log_file, 'a') as f:
            for sample in self.samples:
                f.write(json.dumps(sample) + '\n')
        
        print(f"\n💾 Saved {len(self.samples)} samples to {self.log_file}")


# Example usage
if __name__ == "__main__":
    monitor = GPUMonitor()
    
    # Check availability
    info = monitor.check_availability()
    print(f"GPU Available: {info.get('available')}")
    if info.get('available'):
        print(f"Device: {info['device_name']}")
    
    # Monitor a workload
    # monitor.monitor_workload(duration_seconds=60, interval_seconds=2)
    
    # Or manually sample
    monitor.start_monitoring()
    
    # ... your PDF ingestion or other GPU workload here ...
    time.sleep(5)  # Simulate work
    
    monitor.sample()
    monitor.print_report()
    monitor.save_log()