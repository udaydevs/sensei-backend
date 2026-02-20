"""Indexing Pipeline"""
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import settings

def build_index():
    """
    Used to build indexes, just 
    need to give the path of the pdf document
    """
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-large-en-v1.5"
    )

    client = QdrantClient(
            url=settings.QDRANT_DB_HOST,
            api_key=settings.QDRANT_DB_API_KEY
        )
    if settings.QDRANT_DB_COLLECTION not in [
        c.name for c in client.get_collections().collections
    ]:
        client.create_collection(
            collection_name=settings.QDRANT_DB_COLLECTION,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE
            ),
        )
    vector_store = QdrantVectorStore(
        collection_name=settings.QDRANT_DB_COLLECTION,
        client=client
    )

    documents = SimpleDirectoryReader('data').load_data()

    VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store
    )
    print(client.count(settings.QDRANT_DB_COLLECTION))
    print("Indexing Done Successfully")
