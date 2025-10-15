"""
Document Converter with Docling
Converts PDF, MD, and TXT files to Markdown format with optional OCR support
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

# Supported OCR engines
SUPPORTED_OCR_ENGINES = {"tesseract", "easyocr", "rapidocr"}
SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}

# Global converter instance (cached for performance)
_converter: Optional[DocumentConverter] = None


def get_converter() -> DocumentConverter:
    """
    Return cached DocumentConverter instance for better performance.
    Creates instance only once and reuses it for multiple conversions.
    """
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter


def validate_file(file_path: str) -> Path:
    """
    Validate file existence and format.

    Args:
        file_path: Path to the file

    Returns:
        Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    path = Path(file_path)

    if not path.is_file():
        # Check if path is relative and suggest absolute path
        abs_path = path.absolute()
        raise FileNotFoundError(
            f"File not found: {file_path}\n"
            f"Absolute path checked: {abs_path}\n"
            f"Current directory: {Path.cwd()}\n"
            f"Hint: Check if the file exists and the path is correct"
        )

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format: {path.suffix}\n"
            f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    return path


def validate_ocr_engine(ocr_engine: Optional[str]) -> Optional[str]:
    """
    Validate OCR engine name.

    Args:
        ocr_engine: OCR engine name

    Returns:
        Validated OCR engine name (lowercase)

    Raises:
        ValueError: If OCR engine is not supported
    """
    if ocr_engine is None:
        return None

    ocr_lower = ocr_engine.lower()
    if ocr_lower not in SUPPORTED_OCR_ENGINES:
        raise ValueError(
            f"Unsupported OCR engine: {ocr_engine}\n"
            f"Supported engines: {', '.join(sorted(SUPPORTED_OCR_ENGINES))}"
        )

    return ocr_lower


def convert_to_markdown(
    file_path: str, ocr_engine: Optional[str] = None, debug: bool = False
) -> str:
    """
    Convert document to markdown with optional OCR configuration.

    Args:
        file_path: Path to PDF, MD, or TXT file
        ocr_engine: OCR backend (tesseract, easyocr, rapidocr)
                   Note: OCR engines must be installed separately:
                   - tesseract: Install Tesseract OCR on your system
                   - easyocr: pip install easyocr
                   - rapidocr: pip install rapidocr-onnxruntime
        debug: Enable debug output

    Returns:
        Markdown content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format or OCR engine is invalid, or if conversion fails
    """
    # Validate inputs
    path = validate_file(file_path)
    ocr_engine = validate_ocr_engine(ocr_engine)

    # Setup logging
    logger = logging.getLogger(__name__)
    if debug:
        logger.info(f"Converting file: {path}")
        logger.info(f"File size: {path.stat().st_size:,} bytes")
        logger.info(f"OCR engine: {ocr_engine or 'None'}")

    # Get or create converter with OCR support if needed
    if path.suffix.lower() == ".pdf" and ocr_engine:
        # Select appropriate OCR options class
        if ocr_engine == "tesseract":
            ocr_options = TesseractOcrOptions()
        elif ocr_engine == "easyocr":
            ocr_options = EasyOcrOptions()
        elif ocr_engine == "rapidocr":
            ocr_options = RapidOcrOptions()
        else:
            raise ValueError(f"Unsupported OCR engine: {ocr_engine}")

        # Configure PDF pipeline with OCR
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.ocr_options = ocr_options

        if debug:
            logger.info(f"Using PDF pipeline with OCR enabled ({ocr_engine})")

        # Create converter with OCR-enabled pipeline
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        result = converter.convert(str(path))
    else:
        if debug:
            logger.info("Using standard conversion pipeline")
        converter = get_converter()
        result = converter.convert(str(path))

    # Extract markdown content
    markdown = _extract_markdown(result, debug)

    if not markdown.strip():
        raise ValueError(
            "Conversion failed: No content could be extracted from the document.\n"
            "The document may be empty, corrupted, or in an unsupported format."
        )

    if debug:
        logger.info(f"Successfully extracted {len(markdown):,} characters")
        logger.info(
            f"Preview (first 500 chars):\n{'-' * 60}\n{markdown[:500]}\n{'-' * 60}"
        )

    return markdown


def _extract_markdown(result, debug: bool = False) -> str:
    """
    Extract markdown from conversion result with fallback strategies.

    Args:
        result: Conversion result from DocumentConverter
        debug: Enable debug logging

    Returns:
        Extracted markdown content
    """
    logger = logging.getLogger(__name__)

    # Primary method: Direct export
    try:
        markdown = result.document.export_to_markdown()
        if debug:
            logger.info("Used direct markdown export")
        return markdown
    except AttributeError as e:
        if debug:
            logger.warning(f"Direct export failed: {e}")
            logger.info("Attempting fallback extraction methods")

    # Fallback 1: Extract from pages and elements
    parts = []
    try:
        for page_num, page in enumerate(getattr(result.document, "pages", []), 1):
            for element in getattr(page, "elements", []):
                if text := getattr(element, "text", None):
                    parts.append(text)

        if parts:
            if debug:
                logger.info(
                    f"Extracted content from {page_num} pages using fallback method"
                )
            return "\n\n".join(parts)
    except Exception as e:
        if debug:
            logger.warning(f"Fallback extraction failed: {e}")

    # Fallback 2: Get raw text
    try:
        if hasattr(result, "text"):
            return result.text
        if hasattr(result.document, "text"):
            return result.document.text
    except Exception as e:
        if debug:
            logger.warning(f"Text extraction failed: {e}")

    return ""


def main():
    """Main entry point for command-line usage"""
    import argparse

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Convert documents (PDF, MD, TXT) to Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf --ocr tesseract
  %(prog)s document.pdf -o output.md --debug
  %(prog)s path/to/document.pdf --ocr easyocr -o result.md

OCR Engine Requirements:
  tesseract:  Install Tesseract on your system + set TESSDATA_PREFIX
  easyocr:    pip install easyocr
  rapidocr:   pip install rapidocr-onnxruntime
        """,
    )

    parser.add_argument("input_file", help="Path to input file (PDF, MD, or TXT)")
    parser.add_argument(
        "--ocr",
        choices=sorted(SUPPORTED_OCR_ENGINES),
        default=None,
        help="OCR engine for PDF processing",
    )
    parser.add_argument(
        "-o", "--output", help="Output file path (default: write to stdout)"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose debug output"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.1.0")

    args = parser.parse_args()

    try:
        # Convert document
        markdown = convert_to_markdown(
            args.input_file, ocr_engine=args.ocr, debug=args.debug
        )

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)

            print(f"✓ Successfully saved to: {output_path}")
            print(f"  Size: {len(markdown):,} characters")
        else:
            print(markdown)

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
