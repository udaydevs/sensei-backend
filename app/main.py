"""
This is the main file
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, chatbot, tranlator
from app.core.config import settings
from app.core.startup import llm_manager
from app.core.database import Base, engine
load_dotenv()

app = FastAPI()

app.include_router(auth.router)
app.include_router(tranlator.router)
app.include_router(chatbot.router)


if settings.all_cors_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origin,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Base.metadata.create_all(bind=engine)

@app.get("/check_health")
async def health_check():
    """Check health for production"""
    return {"message" : "Alive!"}

@app.on_event("startup")
async def startup_event():
    """
    This function work on the start of the server
    """
    llm_manager.init()
