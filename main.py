from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from prompt import system_prompt  
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

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

class Prompt(BaseModel):
    prompt: str | None = None


embed_model = GoogleGenAIEmbedding(
    model_name="text-embedding-004",
    embed_batch_size=100,
    api_key=os.getenv('GOOGLE_API_KEY'),
    max_retries=5,
    timeout=40,
)
Settings.embed_model = embed_model

llm = GoogleGenAI(
    model='gemini-2.5-flash-lite',
    api_key=os.getenv('GOOGLE_API_KEY')
)

text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
Settings.text_splitter = text_splitter

client = QdrantClient(
    host=os.getenv('QDRANT_HOST'),
    api_key=os.getenv('QDRANT_API_KEY')
)

collection_name = os.getenv('QDRANT_COLLECTION_NAME')

vector_store = QdrantVectorStore(client=client,collection_name=collection_name)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
query_engine = index.as_query_engine(llm=llm, similarity_top_k=2)


@app.get('/')
async def root():
    return {'message': 'Hello world'}

@app.post('/prompt/')
async def prompt_by_user(prompt: Prompt):


    message = [
        ChatMessage(role='system', content=system_prompt),
        ChatMessage(role='user', content=f"context:\n{query_engine}\n\nuser prompt:\n{prompt.prompt}")
    ]
    response = await llm.achat(messages=message)
    text = response.message.blocks[0].text.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])
    return {'result' : text.strip()} 
