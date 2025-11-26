"""
Web search integration using Tavily API.
"""

from __future__ import annotations

from typing import List, Dict, Optional
import os
import logging
import requests


class WebSearchService:
    """Simple wrapper around Tavily Search API."""

    API_URL = "https://api.tavily.com/search"

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY not found. Add it to backend/.env to enable web search."
            )
        self.api_key = api_key
        self.logger = logging.getLogger("refcheck.websearch")

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        if not query:
            return []

        try:
            response = requests.post(
                self.API_URL,
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": False,
                    "include_images": False,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            self.logger.warning("Tavily search failed: %s", exc)
            return []

        results = []
        for item in data.get("results", []):
            results.append(
                {
                    "title": item.get("title", "Untitled"),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                }
            )
        return results


