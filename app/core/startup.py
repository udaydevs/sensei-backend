from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from app.core.config import settings


class LLMManager:
    """Initializes LLM and Query Engine"""

    def __init__(self):
        self.llm = None
        self.query_engine = None

    def init(self):
        """
        Initialize all AI system components.
        """
        self.llm = GoogleGenAI(
            model=settings.LLM_MODEL_NAME,
            api_key=settings.LLM_API_KEY
        )

        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-large-en-v1.5"
        )

        Settings.text_splitter = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=20
        )

        client = QdrantClient(
            url=settings.QDRANT_DB_URL,
            api_key=settings.QDRANT_DB_API_KEY
        )

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=settings.QDRANT_DB_COLLECTION
        )

        index = VectorStoreIndex.from_vector_store(vector_store)

        self.query_engine = index.as_query_engine(
            llm=self.llm,
            similarity_top_k=3
        )

llm_manager = LLMManager()