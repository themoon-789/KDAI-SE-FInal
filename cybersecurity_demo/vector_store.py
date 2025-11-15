"""
Vector Store Module - Full RAG Implementation
จัดการ Vector Embeddings และ Semantic Search
"""

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import PyPDF2
import docx
import hashlib
from datetime import datetime

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        """
        สร้าง Vector Store ด้วย ChromaDB
        
        Args:
            persist_directory: โฟลเดอร์สำหรับเก็บ Vector Database
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # สร้าง ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # สร้าง collection สำหรับเก็บเอกสาร
        try:
            self.collection = self.client.get_collection("cybersecurity_docs")
            print(f"✅ Loaded existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="cybersecurity_docs",
                metadata={"description": "Cybersecurity knowledge base"}
            )
            print("✅ Created new collection")
        
        # โหลด Embedding Model (ใช้ model ขนาดเล็กเพื่อความเร็ว)
        print("📥 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
    
    def extract_text_from_file(self, filepath: str) -> str:
        """
        แยกข้อความจากไฟล์ (PDF, DOCX, TXT)
        
        Args:
            filepath: path ของไฟล์
            
        Returns:
            ข้อความที่แยกได้
        """
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
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        แบ่งข้อความเป็น chunks เพื่อ embedding
        
        Args:
            text: ข้อความที่จะแบ่ง
            chunk_size: ขนาดของแต่ละ chunk (characters)
            overlap: ส่วนที่ซ้อนทับกัน (characters)
            
        Returns:
            List ของ text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # หาจุดตัดที่ดี (ท้ายประโยค)
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                cut_point = max(last_period, last_newline)
                
                if cut_point > chunk_size * 0.5:  # ถ้าเจอจุดตัดที่ดี
                    chunk = chunk[:cut_point + 1]
                    end = start + cut_point + 1
            
            if chunk.strip():
                chunks.append(chunk.strip())
            
            start = end - overlap
        
        return chunks
    
    def add_document(self, filepath: str, metadata: Dict = None) -> Dict:
        """
        เพิ่มเอกสารเข้า Vector Store
        
        Args:
            filepath: path ของไฟล์
            metadata: ข้อมูลเพิ่มเติม (filename, upload_time, etc.)
            
        Returns:
            ผลลัพธ์การเพิ่มเอกสาร
        """
        # แยกข้อความจากไฟล์
        print(f"📄 Extracting text from {filepath}...")
        text = self.extract_text_from_file(filepath)
        
        if not text or len(text) < 10:
            return {
                'success': False,
                'error': 'No text extracted from file'
            }
        
        # แบ่งเป็น chunks
        print(f"✂️  Chunking text...")
        chunks = self.chunk_text(text)
        print(f"✅ Created {len(chunks)} chunks")
        
        # สร้าง embeddings
        print(f"🧮 Creating embeddings...")
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # สร้าง unique IDs
        file_hash = hashlib.md5(filepath.encode()).hexdigest()[:8]
        ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
        
        # เตรียม metadata
        if metadata is None:
            metadata = {}
        
        filename = os.path.basename(filepath)
        metadatas = [
            {
                'filename': filename,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'upload_time': metadata.get('upload_time', datetime.now().isoformat()),
                'file_path': filepath
            }
            for i in range(len(chunks))
        ]
        
        # เพิ่มเข้า ChromaDB
        print(f"💾 Adding to vector store...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        print(f"✅ Successfully added {len(chunks)} chunks to vector store")
        
        return {
            'success': True,
            'filename': filename,
            'chunks': len(chunks),
            'total_chars': len(text),
            'file_hash': file_hash
        }
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """
        ค้นหาเอกสารที่เกี่ยวข้องด้วย Semantic Search
        
        Args:
            query: คำค้นหา
            n_results: จำนวนผลลัพธ์ที่ต้องการ
            
        Returns:
            ผลการค้นหา
        """
        # สร้าง embedding สำหรับ query
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # ค้นหาใน ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # จัดรูปแบบผลลัพธ์
        formatted_results = {
            'query': query,
            'results': []
        }
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results['results'].append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def get_context_for_query(self, query: str, max_chunks: int = 3) -> str:
        """
        ดึง context จาก Vector Store สำหรับตอบคำถาม (RAG)
        
        Args:
            query: คำถาม
            max_chunks: จำนวน chunks สูงสุดที่จะใช้
            
        Returns:
            Context text สำหรับ LLM
        """
        search_results = self.search(query, n_results=max_chunks)
        
        if not search_results['results']:
            return ""
        
        # รวม context จาก chunks ที่เกี่ยวข้อง
        context_parts = []
        for i, result in enumerate(search_results['results'], 1):
            filename = result['metadata'].get('filename', 'Unknown')
            text = result['text']
            context_parts.append(f"[Document: {filename}]\n{text}")
        
        return "\n\n".join(context_parts)
    
    def get_stats(self) -> Dict:
        """
        ดึงสถิติของ Vector Store
        
        Returns:
            สถิติต่างๆ
        """
        count = self.collection.count()
        
        # นับจำนวนเอกสารที่ไม่ซ้ำ
        if count > 0:
            all_metadata = self.collection.get()['metadatas']
            unique_files = set(m.get('filename', '') for m in all_metadata)
            num_files = len(unique_files)
        else:
            num_files = 0
        
        return {
            'total_chunks': count,
            'total_documents': num_files,
            'collection_name': self.collection.name,
            'embedding_model': 'all-MiniLM-L6-v2'
        }
    
    def delete_document(self, filename: str) -> Dict:
        """
        ลบเอกสารออกจาก Vector Store
        
        Args:
            filename: ชื่อไฟล์ที่จะลบ
            
        Returns:
            ผลการลบ
        """
        # หา IDs ของ chunks ที่เกี่ยวข้อง
        all_data = self.collection.get()
        ids_to_delete = []
        
        for i, metadata in enumerate(all_data['metadatas']):
            if metadata.get('filename') == filename:
                ids_to_delete.append(all_data['ids'][i])
        
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            return {
                'success': True,
                'deleted_chunks': len(ids_to_delete)
            }
        else:
            return {
                'success': False,
                'error': 'Document not found'
            }
    
    def reset(self):
        """ล้างข้อมูลทั้งหมดใน Vector Store"""
        self.client.delete_collection("cybersecurity_docs")
        self.collection = self.client.create_collection(
            name="cybersecurity_docs",
            metadata={"description": "Cybersecurity knowledge base"}
        )
        print("✅ Vector store reset")
