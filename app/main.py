"""
This is the main file
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, chat
from app.core.config import settings
from app.core.startup import llm_manager
from app.core.database import Base, engine
load_dotenv()

app = FastAPI()

app.include_router(auth.router)
app.include_router(chat.router)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.1.14:3000",
    "https://dashboard-mu-neon-70.vercel.app",
    "https://keven-submissive-unmystically.ngrok-free.dev"
]

if settings.all_cors_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Base.metadata.create_all(bind=engine)

@app.get("check_health")
async def health_check():
    """Check health for production"""
    return {"message" : "Alive!"}

@app.on_event("startup")
async def startup_event():
    """
    This function work on the start of the server
    """
    llm_manager.init()



# @app.websocket("/response/")
# async def response(websocket : WebSocket) -> str:
#     """Steaming llm response"""

#     global llm, query_engine

#     await websocket.accept()
#     while True:
#         user_prompt = await websocket.receive_text()

#         message = [
#             ChatMessage(role='system', content=SYSTEM_PROMPT),
#             ChatMessage(
#                 role='user',
#                 content=f"context:\n{query_engine}\n\nuser prompt:\n{user_prompt}")
#         ]
#         stream = await llm.astream_chat(message)
#         async for chunk in stream:
#             text = chunk.delta or ""
#             if text:
#                 await websocket.send_text(text)

#         await websocket.send_text("[[END]]")
