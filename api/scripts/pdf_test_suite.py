"""
PDF Ingestion Test Suite with GPU Monitoring
Tests PDF pipeline end-to-end with performance metrics
"""

import time
from pathlib import Path

import torch
from docling.document_converter import DocumentConverter


class PDFIngestTester:
    def __init__(self, test_pdf_path: str):
        self.test_pdf = Path(test_pdf_path)
        self.results = {}

    def check_gpu_status(self):
        """Verify GPU is available and get baseline metrics"""
        print("🔍 GPU Status Check")
        print(f"  CUDA Available: {torch.cuda.is_available()}")

        if torch.cuda.is_available():
            print(f"  GPU Name: {torch.cuda.get_device_name(0)}")
            print(
                f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
            )

            # Baseline memory
            torch.cuda.reset_peak_memory_stats()
            baseline = torch.cuda.memory_allocated() / 1e6
            print(f"  Baseline Memory: {baseline:.2f} MB")
            return baseline
        return 0

    def test_pdf_ingestion(self):
        """Test PDF ingestion with timing and error handling"""
        print(f"\n📄 Testing PDF: {self.test_pdf.name}")

        if not self.test_pdf.exists():
            print(f"❌ File not found: {self.test_pdf}")
            return None

        try:
            # Use default DocumentConverter with automatic GPU detection
            converter = DocumentConverter()

            # Time the conversion
            start_time = time.time()
            result = converter.convert(str(self.test_pdf))
            elapsed = time.time() - start_time

            # Extract metrics
            self.results["elapsed_time"] = elapsed
            self.results["success"] = True
            self.results["page_count"] = (
                len(result.document.pages)
                if hasattr(result.document, "pages")
                else "N/A"
            )

            print("✅ Ingestion successful")
            print(f"  Time: {elapsed:.2f}s")
            print(f"  Pages: {self.results['page_count']}")
            print(f"  Target: < 2s per doc {'✅' if elapsed < 2 else '⚠️'}")

            # Test markdown export
            try:
                markdown = result.document.export_to_markdown()
                print(f"  Markdown Export: ✅ ({len(markdown)} chars)")
                self.results["markdown_export"] = True
            except AttributeError as e:
                print(f"  Markdown Export: ⚠️ {str(e)}")
                self.results["markdown_export"] = False
                self.results["export_error"] = str(e)

            return result

        except Exception as e:
            print(f"❌ Ingestion failed: {str(e)}")
            self.results["success"] = False
            self.results["error"] = str(e)
            return None

    def monitor_gpu_memory(self, baseline: float):
        """Check GPU memory usage after processing"""
        if torch.cuda.is_available():
            peak = torch.cuda.max_memory_allocated() / 1e6
            current = torch.cuda.memory_allocated() / 1e6

            print("\n🎮 GPU Memory Usage")
            print(f"  Baseline: {baseline:.2f} MB")
            print(f"  Peak: {peak:.2f} MB")
            print(f"  Current: {current:.2f} MB")
            print(f"  Delta: {peak - baseline:.2f} MB")

            self.results["gpu_baseline"] = baseline
            self.results["gpu_peak"] = peak
            self.results["gpu_delta"] = peak - baseline

    def generate_report(self):
        """Generate shift report entry"""
        print("\n" + "=" * 60)
        print("📊 SHIFT REPORT ENTRY")
        print("=" * 60)

        status = "✅" if self.results.get("success") else "❌"
        print(f"\nPDF Ingestion Test: {status}")

        if self.results.get("success"):
            elapsed = self.results["elapsed_time"]
            target_met = "✅" if elapsed < 2 else "⚠️"
            print(f"  • Latency: {elapsed:.2f}s {target_met}")
            print(f"  • Pages: {self.results['page_count']}")

            if self.results.get("markdown_export"):
                print("  • Markdown Export: ✅ Working")
            else:
                print("  • Markdown Export: ⚠️ Needs patch")
                print(f"    Error: {self.results.get('export_error', 'Unknown')}")

            if torch.cuda.is_available():
                print(
                    f"  • GPU Memory Delta: {self.results.get('gpu_delta', 0):.2f} MB"
                )
        else:
            print(f"  • Error: {self.results.get('error', 'Unknown')}")

        return self.results


# Example usage
if __name__ == "__main__":
    tester = PDFIngestTester("path/to/your/test.pdf")

    # Run full test suite
    baseline = tester.check_gpu_status()
    result = tester.test_pdf_ingestion()
    tester.monitor_gpu_memory(baseline)

    # Generate report
    report_data = tester.generate_report()
