import os
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Import node implementations
from src.nodes.calendar_node import add_event
from src.nodes.search_node import web_search

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class CalendarEventRequest(BaseModel):
    summary: str
    start_iso: str = Field(..., description="ISO 8601 start datetime (e.g. 2026-06-25T14:00:00Z)")
    end_iso: str = Field(..., description="ISO 8601 end datetime")
    location: Optional[str] = None
    description: Optional[str] = None

class CalendarEventResponse(BaseModel):
    id: str
    htmlLink: str
    summary: str
    start: dict
    end: dict

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    query: str
    results: List[Dict]

class AgentRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    response: str

# Calendar event endpoint
@app.post("/calendar/event", response_model=CalendarEventResponse)
def create_event(event: CalendarEventRequest):
    try:
        # Use calendar_node's add_event function
        result = add_event(
            summary=event.summary,
            start_iso=event.start_iso,
            end_iso=event.end_iso,
            location=event.location,
            description=event.description
        )
        return CalendarEventResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Server error

# Tavily search endpoint
@app.post("/search", response_model=SearchResponse)
def tavily_search(request: SearchRequest):
    try:
        # Use search_node's web_search function
        results = web_search(request.query)
        return SearchResponse(query=request.query, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Server error

# Agent endpoint
@app.post("/agent", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    try:
        from src.agent import agent_executor
        from langchain_core.messages import HumanMessage
        
        # Invoke the LangGraph agent
        result = agent_executor.invoke({"messages": [HumanMessage(content=request.query)]})
        
        # Get the final message content from the agent's response
        final_message = result["messages"][-1].content
        return AgentResponse(response=final_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))