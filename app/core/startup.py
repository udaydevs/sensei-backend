"""The function that are going to run on startup"""
import os
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

llm = None
query_engine = None

class LLMManager():
    """Here the llm and query engines are defined"""
    def __init__(self):
        self.llm = None
        self.query_engine = None

    def init(self):
        """Run when the server starts"""

        self.llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        Settings.embed_model = GoogleGenAIEmbedding(
            model_name="text-embedding-004",
            embed_batch_size=100,
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=5,
            timeout=40,
        )

        Settings.text_splitter = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=20
        )

        client = QdrantClient(
            host=os.getenv("QDRANT_HOST"),
            api_key=os.getenv("QDRANT_API_KEY")
        )

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=os.getenv("QDRANT_COLLECTION_NAME")
        )

        index = VectorStoreIndex.from_vector_store(vector_store)
        self.query_engine = index.as_query_engine(
            llm=self.llm,
            similarity_top_k=2,
            vector_store_query_mode="hybrid"
        )

llm_manager = LLMManager()
