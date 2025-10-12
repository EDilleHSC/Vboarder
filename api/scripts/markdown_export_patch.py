"""
Workaround for ConversionResult.export_to_markdown bug
Provides multiple export strategies
"""

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from pathlib import Path
import json


class MarkdownExporter:
    """Handle markdown export with fallback strategies"""
    
    def __init__(self, conversion_result):
        self.result = conversion_result
        self.document = conversion_result.document
    
    def export_method_1_direct(self):
        """Try direct export_to_markdown method"""
        try:
            return self.document.export_to_markdown()
        except AttributeError:
            return None
    
    def export_method_2_manual(self):
        """Manual markdown construction from document structure"""
        try:
            markdown_parts = []
            
            if hasattr(self.document, 'title') and self.document.title:
                markdown_parts.append(f"# {self.document.title}\n")
            
            if hasattr(self.document, 'pages'):
                for page_idx, page in enumerate(self.document.pages, 1):
                    markdown_parts.append(f"\n## Page {page_idx}\n")
                    
                    if hasattr(page, 'elements'):
                        for element in page.elements:
                            if hasattr(element, 'text'):
                                markdown_parts.append(f"{element.text}\n")
            
            elif hasattr(self.document, 'text'):
                markdown_parts.append(self.document.text)
            
            return "\n".join(markdown_parts)
            
        except Exception as e:
            print(f"Method 2 failed: {e}")
            return None
    
    def export_with_fallback(self):
        """Try all export methods in order"""
        result = self.export_method_1_direct()
        if result:
            return result
        
        result = self.export_method_2_manual()
        if result:
            return result
        
        return "# Export Failed\n\nCould not extract markdown from document."


def safe_convert_to_markdown(file_path: str) -> str:
    """Convert document and safely export to markdown"""
    converter = DocumentConverter()
    result = converter.convert(file_path)
    
    exporter = MarkdownExporter(result)
    markdown = exporter.export_with_fallback()
    
    return markdown


if __name__ == "__main__":
    test_file = "path/to/test.pdf"
    markdown = safe_convert_to_markdown(test_file)
    print(markdown[:500])
