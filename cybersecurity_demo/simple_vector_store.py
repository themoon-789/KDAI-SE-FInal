"""
Simple Vector Store - ไม่ต้องใช้ ChromaDB
ใช้ in-memory storage และ cosine similarity
"""

import os
import PyPDF2
import docx
import hashlib
import json
from datetime import datetime
from typing import List, Dict
import numpy as np

class SimpleVectorStore:
    def __init__(self, persist_file="./vector_data.json"):
        """
        สร้าง Simple Vector Store
        
        Args:
            persist_file: ไฟล์สำหรับเก็บข้อมูล
        """
        self.persist_file = persist_file
        self.documents = []  # เก็บเอกสารทั้งหมด
        self.load_data()
        print("✅ Simple Vector Store initialized")
    
    def load_data(self):
        """โหลดข้อมูลจากไฟล์"""
        if os.path.exists(self.persist_file):
            try:
                with open(self.persist_file, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                print(f"✅ Loaded {len(self.documents)} documents")
            except:
                self.documents = []
        else:
            self.documents = []
    
    def save_data(self):
        """บันทึกข้อมูลลงไฟล์"""
        with open(self.persist_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def extract_text_from_file(self, filepath: str) -> str:
        """แยกข้อความจากไฟล์"""
        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if ext == '.pdf':
                return self._extract_from_pdf(filepath)
            elif ext == '.docx':
                return self._extract_from_docx(filepath)
            elif ext == '.txt':
                return self._extract_from_txt(filepath)
            else:
                return f"Unsupported file type: {ext}"
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """แยกข้อความจาก PDF"""
        text = ""
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    def _extract_from_docx(self, filepath: str) -> str:
        """แยกข้อความจาก DOCX"""
        doc = docx.Document(filepath)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    
    def _extract_from_txt(self, filepath: str) -> str:
        """แยกข้อความจาก TXT"""
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read().strip()
    
    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """แบ่งข้อความเป็น chunks"""
        chunks = []
        words = text.split()
        
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            
            if current_length >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def simple_embedding(self, text: str) -> List[float]:
        """
        สร้าง simple embedding (TF-IDF style)
        ในระบบจริงควรใช้ sentence-transformers
        """
        # แปลงเป็นตัวพิมพ์เล็ก
        text = text.lower()
        
        # คำสำคัญด้าน cybersecurity
        keywords = [
            'attack', 'threat', 'vulnerability', 'malware', 'ransomware',
            'phishing', 'firewall', 'encryption', 'security', 'breach',
            'ddos', 'sql injection', 'xss', 'authentication', 'authorization',
            'password', 'network', 'intrusion', 'detection', 'prevention'
        ]
        
        # สร้าง vector จากความถี่ของคำสำคัญ
        vector = []
        for keyword in keywords:
            count = text.count(keyword)
            vector.append(count)
        
        # Normalize
        total = sum(vector) or 1
        vector = [v / total for v in vector]
        
        return vector
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """คำนวณ cosine similarity"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def add_document(self, filepath: str, metadata: Dict = None) -> Dict:
        """เพิ่มเอกสารเข้า Vector Store"""
        print(f"📄 Processing {filepath}...")
        
        # แยกข้อความ
        text = self.extract_text_from_file(filepath)
        
        if not text or len(text) < 10:
            return {
                'success': False,
                'error': 'No text extracted from file'
            }
        
        # แบ่งเป็น chunks
        chunks = self.chunk_text(text)
        print(f"✂️  Created {len(chunks)} chunks")
        
        # สร้าง embeddings
        filename = os.path.basename(filepath)
        file_hash = hashlib.md5(filepath.encode()).hexdigest()[:8]
        
        for i, chunk in enumerate(chunks):
            embedding = self.simple_embedding(chunk)
            
            doc = {
                'id': f"{file_hash}_{i}",
                'filename': filename,
                'text': chunk,
                'embedding': embedding,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'upload_time': metadata.get('upload_time', datetime.now().isoformat()) if metadata else datetime.now().isoformat()
            }
            
            self.documents.append(doc)
        
        # บันทึกข้อมูล
        self.save_data()
        
        print(f"✅ Added {len(chunks)} chunks")
        
        return {
            'success': True,
            'filename': filename,
            'chunks': len(chunks),
            'total_chars': len(text)
        }
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """ค้นหาเอกสารที่เกี่ยวข้อง"""
        if not self.documents:
            return {
                'query': query,
                'results': []
            }
        
        # สร้าง embedding สำหรับ query
        query_embedding = self.simple_embedding(query)
        
        # คำนวณ similarity กับทุก document
        results = []
        for doc in self.documents:
            similarity = self.cosine_similarity(query_embedding, doc['embedding'])
            results.append({
                'text': doc['text'],
                'metadata': {
                    'filename': doc['filename'],
                    'chunk_index': doc['chunk_index'],
                    'total_chunks': doc['total_chunks']
                },
                'distance': 1 - similarity,  # แปลงเป็น distance
                'similarity': similarity
            })
        
        # เรียงตาม similarity (สูงสุดก่อน)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # เอาแค่ top n
        top_results = results[:n_results]
        
        return {
            'query': query,
            'results': top_results
        }
    
    def get_context_for_query(self, query: str, max_chunks: int = 3) -> str:
        """ดึง context สำหรับ RAG"""
        search_results = self.search(query, n_results=max_chunks)
        
        if not search_results['results']:
            return ""
        
        context_parts = []
        for i, result in enumerate(search_results['results'], 1):
            filename = result['metadata'].get('filename', 'Unknown')
            text = result['text']
            context_parts.append(f"[Document: {filename}]\n{text}")
        
        return "\n\n".join(context_parts)
    
    def get_stats(self) -> Dict:
        """ดึงสถิติ"""
        unique_files = set(doc['filename'] for doc in self.documents)
        
        return {
            'total_chunks': len(self.documents),
            'total_documents': len(unique_files),
            'collection_name': 'simple_vector_store',
            'embedding_model': 'simple-tf-idf'
        }
    
    def delete_document(self, filename: str) -> Dict:
        """ลบเอกสาร"""
        initial_count = len(self.documents)
        self.documents = [doc for doc in self.documents if doc['filename'] != filename]
        deleted_count = initial_count - len(self.documents)
        
        if deleted_count > 0:
            self.save_data()
            return {
                'success': True,
                'deleted_chunks': deleted_count
            }
        else:
            return {
                'success': False,
                'error': 'Document not found'
            }
    
    def reset(self):
        """ล้างข้อมูลทั้งหมด"""
        self.documents = []
        self.save_data()
        print("✅ Vector store reset")
