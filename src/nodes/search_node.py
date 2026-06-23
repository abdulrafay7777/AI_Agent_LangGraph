"""Tavily search integration node for the LangGraph agent."""

from __future__ import annotations
import os
from typing import List, Dict

from langchain_tavily import TavilySearch


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Perform a Tavily text search.

    Args:
        query: The search query string.
        max_results: Maximum number of result items to return.

    Returns:
        A list of dicts containing ``title`` and ``href`` for each hit.
    """
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY environment variable not set")
        
    try:
        search_tool = TavilySearch(max_results=max_results)
        results_raw = search_tool.invoke({"query": query})
        
        results: List[Dict[str, str]] = []
        if isinstance(results_raw, list):
            for r in results_raw:
                results.append({
                    "title": r.get("title", ""), 
                    "href": r.get("url", r.get("href", ""))
                })
        else:
            # Fallback if it returns a string
            results.append({"title": "Search Result", "href": "", "content": str(results_raw)})
        return results
    except Exception as exc:
        raise RuntimeError(f"Tavily search failed: {exc}") from exc