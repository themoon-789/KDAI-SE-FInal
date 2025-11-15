"""
Unified Vector Store - รวม Vector Stores หลายแหล่งเข้าด้วยกัน
ค้นหาจากทั้ง Exploit-DB Papers และเอกสารอื่นๆ พร้อมกัน
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

class UnifiedVectorStore:
    def __init__(self, 
                 main_db_path="./chroma_db",
                 exploitdb_path="../chroma_db_exploitdb"):
        """
        สร้าง Unified Vector Store ที่รวมหลาย collections
        
        Args:
            main_db_path: path สำหรับเอกสารทั่วไป
            exploitdb_path: path สำหรับ Exploit-DB papers
        """
        self.main_db_path = main_db_path
        self.exploitdb_path = exploitdb_path
        
        print("🔧 Initializing Unified Vector Store...")
        
        # โหลด Embedding Model (ใช้ร่วมกัน)
        print("📥 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Embedding model loaded")
        
        # สร้าง ChromaDB clients
        self._init_main_db()
        self._init_exploitdb()
        
        print("✅ Unified Vector Store ready!")
    
    def _init_main_db(self):
        """เริ่มต้น main database (เอกสารทั่วไป)"""
        os.makedirs(self.main_db_path, exist_ok=True)
        
        self.main_client = chromadb.PersistentClient(
            path=self.main_db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        try:
            self.main_collection = self.main_client.get_collection("cybersecurity_docs")
            print(f"✅ Main DB: {self.main_collection.count()} documents")
        except:
            self.main_collection = self.main_client.create_collection(
                name="cybersecurity_docs",
                metadata={"description": "General cybersecurity documents"}
            )
            print("✅ Main DB: Created new collection")
    
    def _init_exploitdb(self):
        """เริ่มต้น Exploit-DB database"""
        if not os.path.exists(self.exploitdb_path):
            print("⚠️  Exploit-DB not found (run import_exploitdb_papers.py first)")
            self.exploitdb_collection = None
            return
        
        self.exploitdb_client = chromadb.PersistentClient(
            path=self.exploitdb_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        try:
            self.exploitdb_collection = self.exploitdb_client.get_collection("exploitdb_papers")
            print(f"✅ Exploit-DB: {self.exploitdb_collection.count()} documents")
        except:
            print("⚠️  Exploit-DB collection not found")
            self.exploitdb_collection = None
    
    def search(self, query: str, n_results: int = 5, sources: List[str] = None) -> Dict:
        """
        ค้นหาจากทุก sources
        
        Args:
            query: คำค้นหา
            n_results: จำนวนผลลัพธ์ต่อ source
            sources: list ของ sources ที่ต้องการค้นหา ['main', 'exploitdb']
                    ถ้าเป็น None จะค้นหาทุก source
        
        Returns:
            Dict ที่มีผลลัพธ์จากแต่ละ source
        """
        if sources is None:
            sources = ['main', 'exploitdb']
        
        # สร้าง embedding สำหรับ query
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = {
            'query': query,
            'sources': {}
        }
        
        # ค้นหาจาก main database
        if 'main' in sources and self.main_collection:
            try:
                main_results = self.main_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                results['sources']['main'] = {
                    'count': len(main_results['documents'][0]),
                    'documents': main_results['documents'][0],
                    'metadatas': main_results['metadatas'][0],
                    'distances': main_results['distances'][0] if 'distances' in main_results else []
                }
            except Exception as e:
                print(f"⚠️  Error searching main DB: {str(e)}")
                results['sources']['main'] = {'count': 0, 'documents': [], 'metadatas': []}
        
        # ค้นหาจาก Exploit-DB
        if 'exploitdb' in sources and self.exploitdb_collection:
            try:
                exploitdb_results = self.exploitdb_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                results['sources']['exploitdb'] = {
                    'count': len(exploitdb_results['documents'][0]),
                    'documents': exploitdb_results['documents'][0],
                    'metadatas': exploitdb_results['metadatas'][0],
                    'distances': exploitdb_results['distances'][0] if 'distances' in exploitdb_results else []
                }
            except Exception as e:
                print(f"⚠️  Error searching Exploit-DB: {str(e)}")
                results['sources']['exploitdb'] = {'count': 0, 'documents': [], 'metadatas': []}
        
        return results
    
    def search_combined(self, query: str, n_results: int = 10) -> List[Dict]:
        """
        ค้นหาและรวมผลลัพธ์จากทุก sources เรียงตาม relevance
        
        Args:
            query: คำค้นหา
            n_results: จำนวนผลลัพธ์ทั้งหมดที่ต้องการ
        
        Returns:
            List ของผลลัพธ์ที่เรียงตาม relevance score
        """
        # ค้นหาจากทุก source
        results = self.search(query, n_results=n_results)
        
        # รวมผลลัพธ์
        combined = []
        
        for source_name, source_data in results['sources'].items():
            for i, (doc, metadata) in enumerate(zip(source_data['documents'], source_data['metadatas'])):
                distance = source_data['distances'][i] if source_data['distances'] else 0
                
                combined.append({
                    'source': source_name,
                    'document': doc,
                    'metadata': metadata,
                    'distance': distance,
                    'relevance_score': 1 / (1 + distance)  # แปลง distance เป็น score
                })
        
        # เรียงตาม relevance score
        combined.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return combined[:n_results]
    
    def add_document(self, 
                    filepath: str, 
                    metadata: Dict = None,
                    collection: str = 'main') -> bool:
        """
        เพิ่มเอกสารเข้า vector store
        
        Args:
            filepath: path ของไฟล์
            metadata: metadata เพิ่มเติม
            collection: 'main' หรือ 'exploitdb'
        
        Returns:
            True ถ้าสำเร็จ
        """
        if collection == 'main':
            target_collection = self.main_collection
        elif collection == 'exploitdb':
            target_collection = self.exploitdb_collection
        else:
            print(f"❌ Unknown collection: {collection}")
            return False
        
        if not target_collection:
            print(f"❌ Collection '{collection}' not available")
            return False
        
        try:
            # แยกข้อความจากไฟล์
            text = self._extract_text_from_file(filepath)
            
            if not text:
                print(f"❌ Could not extract text from {filepath}")
                return False
            
            # แบ่ง text เป็น chunks
            chunks = self._chunk_text(text)
            
            # สร้าง document ID
            doc_id = hashlib.md5(filepath.encode()).hexdigest()
            
            # เตรียม metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'filename': os.path.basename(filepath),
                'filepath': filepath,
                'added_date': datetime.now().isoformat(),
                'source': collection
            })
            
            # เพิ่มแต่ละ chunk
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                embedding = self.embedding_model.encode(chunk).tolist()
                
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
                
                target_collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[chunk_metadata]
                )
            
            print(f"✅ Added {len(chunks)} chunks from {os.path.basename(filepath)}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding document: {str(e)}")
            return False
    
    def _extract_text_from_file(self, filepath: str) -> str:
        """แยกข้อความจากไฟล์"""
        ext = os.path.splitext(filepath)[1].lower()
        
        try:
            if ext == '.pdf':
                return self._extract_from_pdf(filepath)
            elif ext == '.docx':
                return self._extract_from_docx(filepath)
            elif ext in ['.txt', '.md']:
                return self._extract_from_txt(filepath)
            else:
                return ""
        except Exception as e:
            print(f"⚠️  Error extracting text: {str(e)}")
            return ""
    
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
        """แยกข้อความจาก TXT/MD"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as file:
                    return file.read().strip()
            except:
                continue
        return ""
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """แบ่งข้อความเป็น chunks"""
        if not text or len(text) < chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end < len(text):
                newline_pos = text.rfind('\n', start, end)
                if newline_pos > start:
                    end = newline_pos
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    def get_stats(self) -> Dict:
        """แสดงสถิติของทุก collections"""
        stats = {
            'main': {
                'total_chunks': self.main_collection.count() if self.main_collection else 0
            },
            'exploitdb': {
                'total_chunks': self.exploitdb_collection.count() if self.exploitdb_collection else 0
            }
        }
        
        return stats
    
    def print_stats(self):
        """แสดงสถิติแบบสวยงาม"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("📊 Vector Store Statistics")
        print("=" * 60)
        print(f"Main Database:      {stats['main']['total_chunks']:,} chunks")
        print(f"Exploit-DB Papers:  {stats['exploitdb']['total_chunks']:,} chunks")
        print(f"Total:              {stats['main']['total_chunks'] + stats['exploitdb']['total_chunks']:,} chunks")
        print("=" * 60 + "\n")


def demo_search():
    """ตัวอย่างการใช้งาน"""
    print("=" * 60)
    print("  Unified Vector Store - Demo")
    print("=" * 60)
    
    # สร้าง store
    store = UnifiedVectorStore()
    
    # แสดงสถิติ
    store.print_stats()
    
    # ทดสอบค้นหา
    queries = [
        "SQL injection techniques",
        "buffer overflow exploitation",
        "XSS attack prevention"
    ]
    
    for query in queries:
        print(f"\n🔍 Searching: '{query}'")
        print("-" * 60)
        
        results = store.search_combined(query, n_results=5)
        
        for i, result in enumerate(results, 1):
            source = result['source']
            metadata = result['metadata']
            doc = result['document']
            score = result['relevance_score']
            
            print(f"\n{i}. [{source.upper()}] Score: {score:.3f}")
            
            if source == 'exploitdb':
                print(f"   Title: {metadata.get('title', 'Untitled')}")
                print(f"   Author: {metadata.get('author', 'Unknown')}")
            else:
                print(f"   File: {metadata.get('filename', 'Unknown')}")
            
            print(f"   Preview: {doc[:150]}...")
        
        print()


if __name__ == "__main__":
    demo_search()
