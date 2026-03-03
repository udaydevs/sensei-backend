import uuid
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.prompts.chat import CHAT_SYSTEM_PROMPT
from app.core.startup import llm_manager
from app.core.config import settings

load_dotenv()

router = APIRouter(prefix='/chatbot')

model = GoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=settings.LLM_API_KEY
)

checkpointer = InMemorySaver()

class ChatBot(TypedDict):
    """State for chatbot graph"""
    messages: Annotated[list[BaseMessage], add_messages]
    context: str

def context_node(state: ChatBot):
    """Retrieve context from RAG engine"""
    user_message = state["messages"][-1].content

    rag_result = llm_manager.query_engine.query(user_message)
    return {"context": str(rag_result)}

def llm_node(state: ChatBot):
    """Generate response using LLM with retrieved context"""
    messages = state["messages"]

    system_prompt = f"{CHAT_SYSTEM_PROMPT}\n\nContext: {state['context']}"

    response = model.invoke(
        [
            {"role": "system", "content": system_prompt},
            *[
                {
                    "role": "user" if hasattr(m, "content") and isinstance(m, HumanMessage) else "assistant",
                    "content": m.content
                }
                for m in messages
            ]
        ]
    )

    return {"messages": [AIMessage(content=response)]}

graph = StateGraph(ChatBot)
graph.add_node("context_node", context_node)
graph.add_node("llm_node", llm_node)
graph.add_edge(START, "context_node")
graph.add_edge("context_node", "llm_node")
graph.add_edge("llm_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

@router.websocket("/talk")
async def conversation(websocket: WebSocket):
    """
    Talk route inbuilt with streaming service
    """
    await websocket.accept()

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        while True:
            user_prompt = await websocket.receive_text()

            async for message, metadata in chatbot.astream(
                {"messages": [HumanMessage(content=user_prompt)]},
                config=config,
                stream_mode="messages"
            ):
                if isinstance(message, AIMessage) and message.content:
                    await websocket.send_text(message.content)

    except WebSocketDisconnect:
        print("Client disconnected")
