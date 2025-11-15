"""
ทดสอบ Unified Vector Store
"""
from unified_vector_store import UnifiedVectorStore

print('🧪 Testing Unified Vector Store...\n')

# สร้าง store
store = UnifiedVectorStore()

# แสดงสถิติ
store.print_stats()

# ทดสอบค้นหา
queries = [
    'SQL injection',
    'XSS attack',
    'buffer overflow'
]

for query in queries:
    print(f'\n🔍 Searching: "{query}"')
    print('-' * 60)
    
    results = store.search_combined(query, n_results=3)
    
    if not results:
        print('   No results found')
        continue
    
    for i, r in enumerate(results, 1):
        source = r['source'].upper()
        score = r['relevance_score']
        title = r['metadata'].get('title', 'N/A')
        preview = r['document'][:100]
        
        print(f'\n{i}. [{source}] Score: {score:.3f}')
        print(f'   Title: {title}')
        print(f'   Preview: {preview}...')

print('\n✅ Test completed!')
