"""Routes for chat application"""
from llama_index.core.prompts import ChatMessage
from fastapi import APIRouter, HTTPException, WebSocket, status
from app.models.user_prompt import Prompt
from app.prompts.chat import CHAT_SYSTEM_PROMPT
from app.prompts.prompt import SYSTEM_PROMPT
from app.core.startup import llm_manager

router = APIRouter(
    prefix='/chat'
)

@router.post("/translator")
async def prompt_by_user(prompt: Prompt):
    """
    Tranlation route which takes input from user and generate a detailed translation
    """
    if not llm_manager.llm or not llm_manager.query_engine:
        raise HTTPException(
            detail='LLM is not working properly',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    message = [
        ChatMessage(role='system', content=SYSTEM_PROMPT),
        ChatMessage(
            role='user',
            content=f"context:\n{llm_manager.query_engine}\n\nuser prompt:\n{prompt.prompt}")
    ]
    resp = await llm_manager.llm.achat(messages=message)
    text = resp.message.blocks[0].text.strip()

    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])
    return text.strip()

@router.websocket("/talk")
async def conversation(websocket: WebSocket) -> str:
    """
    Chat route which used for one to one communication with user
    """
    if not llm_manager.llm or not llm_manager.query_engine:
        raise HTTPException(
            detail='LLM is not working properly',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    await websocket.accept()
    while True:
        user_prompt = await websocket.receive_text()

        message = [
            ChatMessage(role='system', content=CHAT_SYSTEM_PROMPT),
            ChatMessage(
                role='user',
                content=f"context:\n{llm_manager.query_engine}\n\nuser prompt:\n{user_prompt}")
        ]

        stream = await llm_manager.llm.astream_chat(message)
        async for chunk in stream:
            text = chunk.delta or ""
            if text:
                await websocket.send_text(text)

