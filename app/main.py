"""
This is the main file
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from app.models.promt_model import Prompt
from app.prompt import SYSTEM_PROMPT
load_dotenv()

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.1.14:3000",
    "https://dashboard-mu-neon-70.vercel.app",
    "https://keven-submissive-unmystically.ngrok-free.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

query_engine = None
llm = None


@app.on_event("startup")
async def startup_event():
    """
    This function work on the start of the server
    """
    global llm, query_engine

    llm = GoogleGenAI(
        model='gemini-2.5-flash-lite',
        api_key=os.getenv('GOOGLE_API_KEY')
    )

    embed_model = GoogleGenAIEmbedding(
        model_name="text-embedding-004",
        embed_batch_size=100,
        api_key=os.getenv('GOOGLE_API_KEY'),
        max_retries=5,
        timeout=40,
    )
    Settings.embed_model = embed_model

    text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
    Settings.text_splitter = text_splitter

    client = QdrantClient(
        host=os.getenv('QDRANT_HOST'),
        api_key=os.getenv('QDRANT_API_KEY')
    )

    collection_name = os.getenv('QDRANT_COLLECTION_NAME')
    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=2,
        vector_store_query_mode ='hybrid'
    )



@app.post("/prompt/")
async def prompt_by_user(prompt: Prompt):
    """
    Generation of the solution from the prompt take place here.
    """
    global query_engine, llm

    message = [
        ChatMessage(role='system', content=SYSTEM_PROMPT),
        ChatMessage(
            role='user',
            content=f"context:\n{query_engine}\n\nuser prompt:\n{prompt.prompt}")
    ]
    response = await llm.achat(messages=message)
    text = response.message.blocks[0].text.strip()

    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])
    return text.strip()
