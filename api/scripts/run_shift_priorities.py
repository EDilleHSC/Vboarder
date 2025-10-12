"""
CTO Shift Priorities Master Runner
Executes all priority tasks and generates comprehensive report

Usage:
    python run_shift_priorities.py --test-pdf ceo_test.pdf
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict


class ShiftPrioritiesRunner:
    """Execute all shift priorities and generate consolidated report"""
    
    def __init__(self, test_pdf_path: str = None):
        self.test_pdf = test_pdf_path
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "shift_priorities": []
        }
        
    def priority_1_pdf_ingestion_test(self):
        """Priority 1: Re-test PDF ingestion now that GPU is active"""
        print("\n" + "="*60)
        print("🔍 PRIORITY 1: PDF Ingestion Test")
        print("="*60)
        
        if not self.test_pdf:
            print("⚠️ No test PDF specified - skipping")
            return {"status": "skipped", "reason": "No test file provided"}
        
        try:
            from pdf_test_suite import PDFIngestTester
            
            tester = PDFIngestTester(self.test_pdf)
            baseline = tester.check_gpu_status()
            result = tester.test_pdf_ingestion()
            tester.monitor_gpu_memory(baseline)
            report = tester.generate_report()
            
            return {
                "priority": 1,
                "name": "PDF Ingestion Test",
                "status": "completed",
                "success": report.get('success', False),
                "details": report
            }
            
        except Exception as e:
            return {
                "priority": 1,
                "name": "PDF Ingestion Test",
                "status": "error",
                "error": str(e)
            }
    
    def priority_2_markdown_export_test(self):
        """Priority 2: Patch or bypass ConversionResult.export_to_markdown bug"""
        print("\n" + "="*60)
        print("🔍 PRIORITY 2: Markdown Export Patch Test")
        print("="*60)
        
        if not self.test_pdf:
            print("⚠️ No test PDF specified - skipping")
            return {"status": "skipped"}
        
        try:
            from markdown_export_patch import safe_convert_to_markdown
            
            markdown = safe_convert_to_markdown(self.test_pdf)
            success = markdown and len(markdown) > 0
            
            return {
                "priority": 2,
                "name": "Markdown Export Patch",
                "status": "completed",
                "success": success,
                "details": {
                    "export_successful": success,
                    "markdown_length": len(markdown) if markdown else 0
                }
            }
            
        except Exception as e:
            return {
                "priority": 2,
                "name": "Markdown Export Patch",
                "status": "error",
                "error": str(e)
            }
    
    def priority_3_gpu_monitoring(self, duration: int = 30):
        """Priority 3: Monitor GPU memory usage under load"""
        print("\n" + "="*60)
        print("🔍 PRIORITY 3: GPU Memory Monitoring")
        print("="*60)
        
        try:
            from gpu_monitor import GPUMonitor
            
            monitor = GPUMonitor()
            
            # Check if GPU is available
            info = monitor.check_availability()
            if not info.get('available'):
                return {
                    "priority": 3,
                    "name": "GPU Monitoring",
                    "status": "skipped",
                    "reason": "GPU not available"
                }
            
            # Run monitoring during a workload
            report = monitor.monitor_workload(duration_seconds=duration, interval_seconds=2)
            monitor.save_log()
            
            return {
                "priority": 3,
                "name": "GPU Monitoring",
                "status": "completed",
                "success": True,
                "details": report
            }
            
        except Exception as e:
            return {
                "priority": 3,
                "name": "GPU Monitoring",
                "status": "error",
                "error": str(e)
            }
    
    def priority_4_latency_logging(self):
        """Priority 4: Log ingestion latencies (target < 2s per doc)"""
        print("\n" + "="*60)
        print("🔍 PRIORITY 4: Latency Logging Validation")
        print("="*60)
        
        try:
            from latency_logger import LatencyLogger
            
            logger = LatencyLogger(target_latency=2.0)
            
            # Analyze recent logs
            historical = logger.analyze_log_file(hours=8)  # Last shift
            
            return {
                "priority": 4,
                "name": "Latency Logging",
                "status": "completed",
                "success": True,
                "details": historical
            }
            
        except Exception as e:
            return {
                "priority": 4,
                "name": "Latency Logging",
                "status": "error",
                "error": str(e)
            }
    
    def priority_5_docling_config(self):
        """Priority 5: Reconfigure Docling to auto-detect new doc types"""
        print("\n" + "="*60)
        print("🔍 PRIORITY 5: Docling Configuration")
        print("="*60)
        
        # This would involve actual Docling configuration
        # Placeholder for now
        
        return {
            "priority": 5,
            "name": "Docling Configuration",
            "status": "manual_review_required",
            "notes": "Review Docling config for auto-detection of new doc types"
        }
    
    def priority_6_rt_detr_unittest(self):
        """Priority 6: Add unit test to validate rt_detr_v2 pipeline weekly"""
        print("\n" + "="*60)
        print("🔍 PRIORITY 6: RT-DETR v2 Pipeline Unit Test")
        print("="*60)
        
        try:
            from rt_detr_test import run_weekly_test
            
            exit_code = run_weekly_test()
            
            return {
                "priority": 6,
                "name": "RT-DETR v2 Unit Test",
                "status": "completed",
                "success": exit_code == 0,
                "details": {
                    "exit_code": exit_code,
                    "test_passed": exit_code == 0
                }
            }
            
        except Exception as e:
            return {
                "priority": 6,
                "name": "RT-DETR v2 Unit Test",
                "status": "error",
                "error": str(e)
            }
    
    def run_all_priorities(self):
        """Execute all shift priorities"""
        print("\n" + "="*70)
        print("🚀 EXECUTING SHIFT PRIORITIES")
        print("="*70)
        print(f"Timestamp: {self.results['timestamp']}")
        
        # Run each priority
        priorities = [
            self.priority_1_pdf_ingestion_test,
            self.priority_2_markdown_export_test,
            self.priority_3_gpu_monitoring,
            self.priority_4_latency_logging,
            self.priority_5_docling_config,
            self.priority_6_rt_detr_unittest,
        ]
        
        for priority_func in priorities:
            try:
                result = priority_func()
                self.results["shift_priorities"].append(result)
            except Exception as e:
                print(f"❌ Unexpected error in {priority_func.__name__}: {e}")
                self.results["shift_priorities"].append({
                    "name": priority_func.__name__,
                    "status": "fatal_error",
                    "error": str(e)
                })
        
        return self.results
    
    def generate_shift_report(self):
        """Generate formatted shift report"""
        print("\n" + "="*70)
        print("📋 SHIFT PRIORITIES REPORT")
        print("="*70)
        print(f"\nTimestamp: {self.results['timestamp']}\n")
        
        for i, priority in enumerate(self.results["shift_priorities"], 1):
            name = priority.get("name", "Unknown")
            status = priority.get("status", "unknown")
            success = priority.get("success")
            
            # Status icon
            if status == "completed":
                icon = "✅" if success else "⚠️"
            elif status == "error" or status == "fatal_error":
                icon = "❌"
            elif status == "skipped":
                icon = "⏭️"
            else:
                icon = "❓"
            
            print(f"{i}. {icon} {name}: {status.upper()}")
            
            if priority.get("error"):
                print(f"   Error: {priority['error']}")
            
            if priority.get("details"):
                # Print key details
                details = priority["details"]
                if isinstance(details, dict):
                    for key, val in list(details.items())[:3]:  # Show first 3 details
                        print(f"   • {key}: {val}")
        
        # Summary
        completed = sum(1 for p in self.results["shift_priorities"] if p.get("status") == "completed")
        total = len(self.results["shift_priorities"])
        
        print(f"\n📊 Summary: {completed}/{total} priorities completed")
        
        # Save to file
        report_file = Path(f"shift_priorities_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Full report saved to: {report_file}")
        
        return self.results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run CTO shift priorities")
    parser.add_argument("--test-pdf", help="Path to test PDF file", default=None)
    parser.add_argument("--gpu-monitor-duration", type=int, default=30, 
                       help="GPU monitoring duration in seconds")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = ShiftPrioritiesRunner(test_pdf_path=args.test_pdf)
    
    # Run all priorities
    results = runner.run_all_priorities()
    
    # Generate report
    runner.generate_shift_report()
    
    # Exit with appropriate code
    success_count = sum(1 for p in results["shift_priorities"] 
                       if p.get("success") and p.get("status") == "completed")
    total_count = len(results["shift_priorities"])
    
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())