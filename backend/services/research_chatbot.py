"""
Research assistant chatbot leveraging Groq's LLM API.
"""

from typing import Optional, List, Dict
import os
import requests

from dotenv import load_dotenv

load_dotenv()


class ResearchChatbot:
    """Use Groq-hosted models to answer research questions."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Add it to backend/.env to enable the chatbot."
            )

        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.system_prompt = (
            "You are RefAssist, a knowledgeable research assistant. "
            "You help users summarize papers, explain concepts, and find related work. "
            "When reference text or web snippets are provided, cite them using [n] "
            "and include the actual URL shown in the snippet when sharing links. "
            "If no reference text exists, rely on general knowledge and state that explicitly. "
            "Keep answers structured and concise."
        )

    def chat(
        self,
        question: str,
        reference_text: Optional[str],
        mode: str = "general",
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        if not question:
            raise ValueError("Question is required for chatbot.")

        reference_context = reference_text.strip() if reference_text else "None provided"
        mode = mode or "general"

        messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

        if history:
            for msg in history[-8:]:
                role = msg.get("role")
                content = msg.get("content")
                if role in {"user", "assistant"} and content:
                    messages.append({"role": role, "content": content})

        user_prompt = (
            f"Mode: {mode}\n"
            f"Reference text:\n{reference_context}\n\n"
            f"User question:\n{question}\n\n"
            "Respond with structured paragraphs and cite any numbered web snippets if present."
        )
        messages.append({"role": "user", "content": user_prompt})

        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 1024,
            },
            timeout=60,
        )
        if not response.ok:
            detail = ""
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise RuntimeError(f"Groq API error {response.status_code}: {detail}")
        data = response.json()
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        if not content:
            raise RuntimeError("Chatbot returned an empty response.")
        return content


