"""Chatbot using langgraph"""
import os
from typing import List, TypedDict, Annotated
# from llama_index.core.prompts import ChatMessage
from dotenv import load_dotenv
from fastapi import APIRouter, WebSocket
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import GoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from app.prompts.chat import CHAT_SYSTEM_PROMPT
from app.core.startup import llm_manager
from app.core.config import settings

load_dotenv()

router = APIRouter(
    prefix='/chatbot'
)

model = GoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.LLM_API_KEY
    )
# model = ChatGroq(
#     model="llama-3.1-8b-instant",
#     api_key=os.getenv("GROQ_API_KEY")
# )

class ChatBot(TypedDict):
    """
    Docstring for ChatBot
    """
    message : Annotated[list[BaseMessage], add_messages]
    context : str

def context_node(state: ChatBot):
    """
    Docstring for chat_node
    
    :param state: Description
    :type state: ChatBot
    """
    message = state["message"][-1].content
    rag_result = llm_manager.query_engine.aquery(message)
    return {"context": str(rag_result)}

def llm_node(state: ChatBot):
    """
    Uses LangChain LLM with retrieved context.
    """
    messages = state["message"]

    prompt = [
        HumanMessage(
            content=f"""{CHAT_SYSTEM_PROMPT}Context:{state['context']}"""
        ),*messages,
    ]

    response = model.invoke(prompt)
    return {"message":[response]}

graph = StateGraph(ChatBot)

graph.add_node('context_node', context_node)
graph.add_node('llm_node', llm_node)
graph.add_edge(START, 'context_node')
graph.add_edge('context_node', 'llm_node')
graph.add_edge('llm_node' , END)

chatbot = graph.compile()

@router.websocket("/talk")
async def conversation(websocket: WebSocket) -> str:
    """
    Chat route which used for one to one communication with user
    """


    await websocket.accept()
    state: ChatBot = {
        "message": [HumanMessage(content=CHAT_SYSTEM_PROMPT)],
        "context": "",
    }
    while True:
        user_prompt = await websocket.receive_text()

        # message = [
        #     ChatMessage(role='system', content=CHAT_SYSTEM_PROMPT),
        #     ChatMessage(
        #         role='user',
        #         content=f"context:\n{llm_manager.query_engine}\n\nuser prompt:\n{user_prompt}")
        # ]

        # stream = await llm_manager.llm.astream_chat(message)
        # async for chunk in stream:
        #     text = chunk.delta or ""
        #     if text:
        #         await websocket.send_text(text)
        state["message"].append(
            HumanMessage(content=user_prompt)
        )
        result = chatbot.invoke(state)
        state = result

        ai_message = result["message"][-1]
        await websocket.send_text(ai_message.content)

