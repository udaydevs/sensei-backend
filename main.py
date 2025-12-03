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
from datetime import datetime, timedelta
from fastapi import HTTPException, Security,status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os, jwt

load_dotenv()
app = FastAPI()

security = HTTPBearer()
SECRET_KEY = "alskdjfieansviewh23iu509r4hgvn3g948hbn3984hbnv349"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
 
fake_user_db = {
    'udaysingh' : {'username' : 'udaysingh', 'password' : '#1Engineer'}
}


class Login(BaseModel):
    username : str
    password : str


@app.post('/login/')
async def login_user(user:Login):
    db_user = fake_user_db.get(user.username)
    if not db_user or db_user["password"] != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token_data = {'sub' : user.username}
    token = create_jwt_token(data=token_data)
    return { 'token' : token, 'token_type' : 'Bearer'}
 
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp' : expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

def verify_jwt_token(token: str):
    try:
        decode_token  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decode_token if datetime.utcfromtimestamp(decode_token.get('exp')) >= datetime.utcnow() else None
    except jwt.PyJWTError:
        return None


async def get_current_user(credentials : HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payloads = verify_jwt_token(token=token)
    print(payloads)
    if payloads is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payloads

@app.get('/protected')
async def protected_route(current_user : dict = Depends(get_current_user)):
    return {'msg' : f'Hello, {current_user['sub']}!, You are authenticated.'}

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

query_engine = None
llm = None


@app.on_event("startup")
async def startup_event():
    global query_engine, llm

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

    query_engine = index.as_query_engine(llm=llm, similarity_top_k=2 , vector_store_query_mode ='hybrid' )



@app.post("/prompt/")
async def prompt_by_user(prompt: Prompt):
    global query_engine, llm

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

    return text.strip()
