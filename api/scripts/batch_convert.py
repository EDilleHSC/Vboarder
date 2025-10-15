"""
Batch PDF to Markdown Converter
Converts multiple PDFs in a directory to markdown files
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from docling_convert import convert_to_markdown


def find_pdfs(directory: str, recursive: bool = False) -> List[Path]:
    """
    Find all PDF files in a directory.

    Args:
        directory: Directory to search
        recursive: Search subdirectories recursively

    Returns:
        List of PDF file paths
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not dir_path.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    if recursive:
        pdf_files = list(dir_path.rglob("*.pdf"))
    else:
        pdf_files = list(dir_path.glob("*.pdf"))

    return sorted(pdf_files)


def convert_batch(
    pdf_files: List[Path],
    output_dir: str,
    ocr_engine: str = None,
    debug: bool = False,
    skip_errors: bool = True,
) -> Tuple[int, int, List[str]]:
    """
    Convert multiple PDF files to markdown.

    Args:
        pdf_files: List of PDF file paths
        output_dir: Output directory for markdown files
        ocr_engine: OCR engine to use
        debug: Enable debug output
        skip_errors: Continue on errors instead of stopping

    Returns:
        Tuple of (successful, failed, error_messages)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    successful = 0
    failed = 0
    errors = []

    print(f"\n{'='*60}")
    print(f"Starting batch conversion of {len(pdf_files)} files")
    print(f"Output directory: {output_path}")
    if ocr_engine:
        print(f"OCR engine: {ocr_engine}")
    print(f"{'='*60}\n")

    for i, pdf_file in enumerate(pdf_files, 1):
        # Create output filename
        output_file = output_path / f"{pdf_file.stem}.md"

        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")

        try:
            # Convert the PDF
            markdown = convert_to_markdown(
                str(pdf_file), ocr_engine=ocr_engine, debug=debug
            )

            # Save the output
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown)

            successful += 1
            print(f"  ✓ Success: {output_file.name} ({len(markdown):,} chars)\n")

        except Exception as e:
            failed += 1
            error_msg = f"{pdf_file.name}: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ Failed: {str(e)}\n")

            if not skip_errors:
                raise

    return successful, failed, errors


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert PDF files to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input_folder/
  %(prog)s input_folder/ -o output_folder/
  %(prog)s . --recursive --ocr easyocr
  %(prog)s pdfs/ -o markdown/ --ocr tesseract --debug
        """,
    )

    parser.add_argument("input_dir", help="Input directory containing PDF files")
    parser.add_argument(
        "-o",
        "--output",
        default="markdown_output",
        help="Output directory for markdown files (default: markdown_output)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search subdirectories recursively",
    )
    parser.add_argument(
        "--ocr",
        choices=["tesseract", "easyocr", "rapidocr"],
        default=None,
        help="OCR engine for PDF processing",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose debug output"
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop processing on first error (default: skip errors)",
    )

    args = parser.parse_args()

    try:
        # Find all PDFs
        print(f"Searching for PDFs in: {args.input_dir}")
        if args.recursive:
            print("  (including subdirectories)")

        pdf_files = find_pdfs(args.input_dir, args.recursive)

        if not pdf_files:
            print(f"\n⚠ No PDF files found in {args.input_dir}")
            sys.exit(0)

        print(f"Found {len(pdf_files)} PDF file(s)")

        # Convert all PDFs
        successful, failed, errors = convert_batch(
            pdf_files,
            args.output,
            ocr_engine=args.ocr,
            debug=args.debug,
            skip_errors=not args.stop_on_error,
        )

        # Print summary
        print(f"\n{'='*60}")
        print("Batch Conversion Complete")
        print(f"{'='*60}")
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print(f"Total: {len(pdf_files)}")

        if errors:
            print(f"\n{'='*60}")
            print("Errors:")
            print(f"{'='*60}")
            for error in errors:
                print(f"  • {error}")

        # Exit with appropriate code
        sys.exit(0 if failed == 0 else 1)

    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
