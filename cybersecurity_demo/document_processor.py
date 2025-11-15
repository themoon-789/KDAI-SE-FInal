"""
Document Processing
Extracts text from various file formats and chunks for RAG
"""
import os
import hashlib
from typing import List, Tuple
import PyPDF2
import docx
import json

class DocumentProcessor:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        """Initialize document processor"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_file(self, filepath: str) -> Tuple[str, List[str], str]:
        """
        Process file and extract text
        
        Returns:
            (full_text, chunks, content_hash)
        """
        file_ext = os.path.splitext(filepath)[1].lower()
        
        # Extract text based on file type
        if file_ext == '.pdf':
            text = self._extract_pdf(filepath)
        elif file_ext in ['.docx', '.doc']:
            text = self._extract_docx(filepath)
        elif file_ext == '.txt':
            text = self._extract_txt(filepath)
        elif file_ext == '.json':
            text = self._extract_json(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Calculate content hash
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Chunk text
        chunks = self._chunk_text(text)
        
        return text, chunks, content_hash
    
    def _extract_pdf(self, filepath: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
        
        return text.strip()
    
    def _extract_docx(self, filepath: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(filepath)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Error reading DOCX: {e}")
        
        return text.strip()
    
    def _extract_txt(self, filepath: str) -> str:
        """Extract text from TXT"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as file:
                text = file.read()
        
        return text.strip()
    
    def _extract_json(self, filepath: str) -> str:
        """Extract text from JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Convert JSON to readable text
                text = json.dumps(data, indent=2)
        except Exception as e:
            raise Exception(f"Error reading JSON: {e}")
        
        return text
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings
                for delimiter in ['. ', '.\n', '! ', '?\n']:
                    last_delimiter = text.rfind(delimiter, start, end)
                    if last_delimiter != -1:
                        end = last_delimiter + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < text_length else text_length
        
        return chunks
    
    def extract_metadata(self, filepath: str) -> dict:
        """Extract metadata from file"""
        stat = os.stat(filepath)
        
        metadata = {
            'file_size': stat.st_size,
            'created_at': stat.st_ctime,
            'modified_at': stat.st_mtime,
            'file_extension': os.path.splitext(filepath)[1]
        }
        
        # Try to extract additional metadata for PDFs
        if filepath.endswith('.pdf'):
            try:
                with open(filepath, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    if pdf_reader.metadata:
                        metadata['pdf_title'] = pdf_reader.metadata.get('/Title', '')
                        metadata['pdf_author'] = pdf_reader.metadata.get('/Author', '')
                        metadata['pdf_pages'] = len(pdf_reader.pages)
            except:
                pass
        
        return metadata
