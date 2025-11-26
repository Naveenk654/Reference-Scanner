"""
PDF text extraction service using PyPDFLoader
"""

from langchain_community.document_loaders import PyPDFLoader
from typing import Optional
import os


class PDFExtractor:
    """Extract text from PDF files"""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string, or None if extraction fails
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Combine all pages
            full_text = "\n\n".join([doc.page_content for doc in documents])
            
            return full_text
        
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return None

