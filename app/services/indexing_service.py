from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.core.config import settings

def build_index():

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-large-en-v1.5"
    )

    client = QdrantClient(
        url=settings.QDRANT_DB_URL,
        api_key=settings.QDRANT_DB_API_KEY
    )

    collection = settings.QDRANT_DB_COLLECTION

    if collection in [c.name for c in client.get_collections().collections]:
        client.delete_collection(collection)

    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection
    )

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    documents = SimpleDirectoryReader('data').load_data()

    print("Docs:", len(documents))

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    print(client.count(collection))
    print("Indexing Done Successfully")
