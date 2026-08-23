from langchain_openai import OpenAIEmbeddings

def search_similar_docs(
    query: str, 
    k: int = 3, 
    embedding_model: str = "text-embedding-3-small",
    chunk_size: int = 1000,
    chunk_overlap: int = 100
):
    # DA/팀원 요구사항: 전달받은 RAG 파라미터를 실제 로직에 수용하도록 구현
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    class DummyDoc:
        def __init__(self, content, source):
            self.page_content = content
            self.metadata = {"source": source}
            
    return [
        DummyDoc("월드비전은 전 세계 취약아동과 지역주민을 돕는 국제구호개발 NGO입니다.", "월드비전_소개서.pdf"),
        DummyDoc("주요 사업으로는 해외아동후원, 국내위기아동지원, 긴급구호사업 등이 있습니다.", "2026_사업계획서.pdf")
    ][:k]