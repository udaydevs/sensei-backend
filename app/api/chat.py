"""Routes for chat application"""
from llama_index.core.prompts import ChatMessage
from fastapi import APIRouter, HTTPException, status
from app.models.user_prompt import Prompt
from app.prompts.prompt import SYSTEM_PROMPT
from app.core.startup import llm_manager

router = APIRouter(
    prefix='/chat'
)

@router.post("/translator")
async def prompt_by_user(prompt: Prompt):
    """
    Generation of the solution from the prompt take place here.
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
