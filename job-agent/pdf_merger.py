"""
PDF Merger — Merge resume and cover letter into single PDF.

Uses PyPDF2 or pypdf library.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def merge_pdfs(resume_path: str, cover_letter_path: str, output_path: str) -> bool:
    """
    Merge resume and cover letter PDFs.
    
    Args:
        resume_path: Path to resume PDF
        cover_letter_path: Path to cover letter PDF
        output_path: Path for merged output PDF
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import PyPDF2
    except ImportError:
        logger.error("PyPDF2 not installed. Install via: pip install PyPDF2")
        return False
    
    try:
        merger = PyPDF2.PdfMerger()
        
        # Add cover letter first
        merger.append(cover_letter_path)
        
        # Add resume
        merger.append(resume_path)
        
        # Write to output
        merger.write(output_path)
        merger.close()
        
        logger.info(f"Merged PDF created: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to merge PDFs: {e}")
        return False


def convert_docx_to_pdf(docx_path: str, output_pdf_path: str) -> bool:
    """
    Convert DOCX to PDF (for cover letter generation).
    
    Args:
        docx_path: Path to DOCX file
        output_pdf_path: Path for output PDF
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from docx2pdf import convert
    except ImportError:
        logger.error("docx2pdf not installed. Install via: pip install docx2pdf")
        return False
    
    try:
        convert(docx_path, output_pdf_path)
        logger.info(f"Converted DOCX to PDF: {output_pdf_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to convert DOCX to PDF: {e}")
        return False
