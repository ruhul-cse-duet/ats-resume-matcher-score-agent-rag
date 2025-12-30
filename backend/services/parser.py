import io
import logging
from pypdf import PdfReader
from docx import Document

logger = logging.getLogger(__name__)

def parse_pdf_bytes(b: bytes) -> str:
    """Parse PDF file with error handling"""
    try:
        reader = PdfReader(io.BytesIO(b))
        texts = []
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    texts.append(text)
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                continue
        
        result = "\n".join(texts)
        if not result.strip():
            raise ValueError("No text content could be extracted from PDF")
        return result
    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        raise ValueError(f"Failed to parse PDF file: {str(e)}")

def parse_docx_bytes(b: bytes) -> str:
    """Parse DOCX file with error handling"""
    try:
        doc = Document(io.BytesIO(b))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        result = "\n".join(paragraphs)
        
        if not result.strip():
            raise ValueError("No text content could be extracted from DOCX")
        return result
    except Exception as e:
        logger.error(f"Error parsing DOCX: {str(e)}")
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")

def parse_text_bytes(b: bytes) -> str:
    """Parse text file with error handling"""
    try:
        # Try UTF-8 first, then fallback to other encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                result = b.decode(encoding)
                if result.strip():
                    return result
            except (UnicodeDecodeError, AttributeError):
                continue
        
        raise ValueError("Could not decode text file with any supported encoding")
    except Exception as e:
        logger.error(f"Error parsing text file: {str(e)}")
        raise ValueError(f"Failed to parse text file: {str(e)}")

def parse_upload(upload_file) -> str:
    """Parse uploaded file with comprehensive error handling"""
    try:
        if not upload_file or not upload_file.filename:
            raise ValueError("Invalid file upload")
        
        content = upload_file.file.read()
        if not content:
            raise ValueError("File is empty")
        
        name = upload_file.filename.lower()
        
        if name.endswith(".pdf"):
            return parse_pdf_bytes(content)
        elif name.endswith(".docx"):
            return parse_docx_bytes(content)
        elif name.endswith((".txt", ".text")):
            return parse_text_bytes(content)
        else:
            # Try text parsing as fallback
            logger.warning(f"Unknown file type: {name}, attempting text parse")
            return parse_text_bytes(content)
            
    except Exception as e:
        logger.error(f"Error in parse_upload: {str(e)}")
        raise
