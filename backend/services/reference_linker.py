"""
Reference linker service to enrich references with missing URLs.
"""

from __future__ import annotations

import logging
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

import requests
from rapidfuzz import fuzz


class ReferenceLinker:
    """
    Attempts to enrich references that do not already contain URLs by:
    1. Extracting explicit arXiv identifiers and turning them into links.
    2. Querying the Crossref API to locate DOI/URL candidates for the reference.
    """

    CROSSREF_ENDPOINT = "https://api.crossref.org/works"
    TITLE_THRESHOLD = 60  # minimum similarity score between reference text and Crossref title

    SERPAPI_ENDPOINT = "https://serpapi.com/search"

    def __init__(
        self,
        enable_search: bool = True,
        max_searches: Optional[int] = None,
        serpapi_keys: Optional[List[str]] = None,
        max_workers: int = 5,
    ):
        self.enable_search = enable_search
        self.max_searches = max_searches
        self.logger = logging.getLogger("refcheck.reference_linker")
        self.serpapi_keys = serpapi_keys or self._load_serpapi_keys()
        self._serpapi_index = 0
        self._serpapi_lock = threading.Lock()
        self.max_workers = max_workers

    def enrich(self, references: List[Dict]) -> List[Dict]:
        """
        Enrich the provided references list with best-effort URLs.
        """
        enriched = [None] * len(references)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {
                executor.submit(self._process_reference, ref): idx
                for idx, ref in enumerate(references)
            }

            for future in as_completed(future_map):
                idx = future_map[future]
                try:
                    enriched[idx] = future.result()
                except Exception as exc:
                    self.logger.error("Reference enrichment failed: %s", exc)
                    enriched[idx] = references[idx]

        return enriched

    @staticmethod
    def _extract_arxiv_links(text: str) -> List[str]:
        """Return arXiv links detected in the reference text."""
        if not text:
            return []

        arxiv_pattern = re.compile(r"arXiv:\s*([a-zA-Z0-9./-]+)", re.IGNORECASE)
        matches = arxiv_pattern.findall(text)
        links = []

        for match in matches:
            identifier = match.strip().rstrip(".,;:")
            if identifier:
                links.append(f"https://arxiv.org/abs/{identifier}")

        return links

    def _search_crossref(self, reference_text: str) -> Optional[str]:
        """Query Crossref for a likely matching DOI/URL."""
        params = {
            "query.bibliographic": reference_text[:300],
            "rows": 3,
        }

        last_error: Optional[str] = None

        for attempt in range(3):  # simple retry loop
            try:
                response = requests.get(
                    self.CROSSREF_ENDPOINT,
                    params=params,
                    timeout=8,
                    headers={"User-Agent": "RefCheck/1.0 (mailto:refcheck@example.com)"},
                )
                response.raise_for_status()
                data = response.json()
                items = data.get("message", {}).get("items", [])
                for item in items:
                    title_list = item.get("title") or []
                    title = title_list[0] if title_list else ""
                    if not title:
                        continue

                    score = fuzz.token_set_ratio(reference_text, title)
                    if score < self.TITLE_THRESHOLD:
                        continue

                    doi = item.get("DOI")
                    item_url = item.get("URL")
                    if doi:
                        return f"https://doi.org/{doi}"
                    if item_url:
                        return item_url

                return None

            except requests.RequestException as exc:
                last_error = str(exc)
                self.logger.warning(
                    "Crossref lookup failed (attempt %s/3): %s", attempt + 1, exc
                )
            except ValueError as exc:
                last_error = str(exc)
                self.logger.warning("Invalid Crossref response: %s", exc)
                break

        if last_error:
            self.logger.warning("Crossref lookup exhausted retries: %s", last_error)

        return None

    def _process_reference(self, ref: Dict) -> Dict:
        ref.setdefault("urls", [])
        ref.setdefault("url_details", [])

        if not ref["urls"]:
            for arxiv_url in self._extract_arxiv_links(ref.get("original_reference", "")):
                self._append_url(ref, arxiv_url, "research")

        if (
            not ref["urls"]
            and self.enable_search
            and ref.get("original_reference")
        ):
            candidate = self._search_crossref(ref["original_reference"])
            if candidate:
                self._append_url(ref, candidate, "suggested")

        if (
            not ref["urls"]
            and self.enable_search
            and ref.get("original_reference")
            and self.serpapi_keys
        ):
            candidate = self._search_serpapi(ref["original_reference"])
            if candidate:
                self._append_url(ref, candidate, "suggested")

        return ref

    def _search_serpapi(self, reference_text: str) -> Optional[str]:
        if not self.serpapi_keys:
            return None

        attempts = min(len(self.serpapi_keys), 5)
        for _ in range(attempts):
            key = self._next_serpapi_key()
            if not key:
                return None

            try:
                response = requests.get(
                    self.SERPAPI_ENDPOINT,
                    params={
                        "engine": "google",
                        "q": reference_text,
                        "num": 4,
                        "api_key": key,
                    },
                    timeout=8,
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("organic_results") or []
                for result in results:
                    title = result.get("title") or ""
                    link = result.get("link")
                    if not title or not link:
                        continue

                    score = fuzz.token_set_ratio(reference_text, title)
                    if score >= self.TITLE_THRESHOLD:
                        return link

            except requests.RequestException as exc:
                self.logger.warning("SerpAPI lookup failed: %s", exc)
            except ValueError as exc:
                self.logger.warning("Invalid SerpAPI response: %s", exc)
                break

        return None

    def _next_serpapi_key(self) -> Optional[str]:
        if not self.serpapi_keys:
            return None
        with self._serpapi_lock:
            key = self.serpapi_keys[self._serpapi_index]
            self._serpapi_index = (self._serpapi_index + 1) % len(self.serpapi_keys)
        return key

    @staticmethod
    def _load_serpapi_keys() -> List[str]:
        keys_env = os.getenv("SERPAPI_KEYS", "")
        if not keys_env:
            return []
        return [key.strip() for key in keys_env.split(",") if key.strip()]

    @staticmethod
    def _append_url(ref: Dict, url: str, source: str) -> None:
        if not url:
            return
        urls = ref.setdefault("urls", [])
        url_details = ref.setdefault("url_details", [])
        if url in urls:
            return
        urls.append(url)
        url_details.append({"url": url, "source": source})

