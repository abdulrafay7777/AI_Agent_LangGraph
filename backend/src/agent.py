import os
from typing import Optional

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.nodes.search_node import web_search
from src.nodes.calendar_node import add_event

@tool
def search_tool(query: str) -> str:
    """Search the web for information using Tavily."""
    try:
        results = web_search(query)
        return str(results)
    except Exception as e:
        return f"Search failed: {e}"

@tool
def calendar_tool(
    summary: str, 
    start_iso: str, 
    end_iso: str, 
    location: Optional[str] = None, 
    description: Optional[str] = None
) -> str:
    """
    Create a new event in the Google Calendar.
    
    Args:
        summary: Title of the event.
        start_iso: ISO 8601 formatted start datetime (e.g. "2026-06-25T14:00:00Z").
        end_iso: ISO 8601 formatted end datetime.
        location: Optional location string.
        description: Optional description/notes for the event.
    """
    try:
        result = add_event(
            summary=summary,
            start_iso=start_iso,
            end_iso=end_iso,
            location=location,
            description=description
        )
        return f"Event created successfully. Link: {result.get('htmlLink', 'No link available')}"
    except Exception as e:
        return f"Failed to create event: {e}"

# List of tools to provide to the agent
tools = [search_tool, calendar_tool]

# Initialize the LLM (Requires GOOGLE_API_KEY in environment)
# Using Gemini 2.5 Flash as requested since Groq hit rate limits
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Create the LangGraph agent
agent_executor = create_react_agent(llm, tools)
