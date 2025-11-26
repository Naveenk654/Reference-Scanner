"""
Citation formatter service leveraging MistralAI to format references
into specific citation styles without altering the underlying data.
"""

from typing import Literal
import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

load_dotenv()

AllowedStyle = Literal["APA", "MLA", "IEEE", "Chicago", "Harvard"]


class CitationFormatter:
    """Format raw reference text into a requested citation style."""

    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "MISTRAL_API_KEY not found. "
                "Create backend/.env with MISTRAL_API_KEY=your-api-key"
            )

        try:
            from langchain_mistralai import ChatMistralAI

            self.llm = ChatMistralAI(
                mistral_api_key=api_key,
                model="mistral-small",
                temperature=0.05,
            )
        except ImportError as exc:
            raise ImportError(
                "langchain-mistralai package is required. "
                "Install it with: pip install langchain-mistralai"
            ) from exc

        self.prompt = PromptTemplate(
            input_variables=["style", "reference"],
            template=(
                "You format citations for a reference web application.\n\n"
                "RULES:\n"
                "- Style can only be: APA, MLA, IEEE, Chicago, Harvard.\n"
                "- NEVER modify the provided reference beyond punctuation/"
                "capitalization rules demanded by the chosen style.\n"
                "- Do NOT invent missing data such as DOI, pages, volume, "
                "authors, or titles.\n"
                "- Output ONLY the formatted citation. No extra words.\n"
                "- Use italics/quotation marks exactly as required by the style.\n\n"
                "STYLE: {style}\n"
                "REFERENCE: {reference}\n\n"
                "Return just the formatted citation:"
            ),
        )

    def format_reference(self, reference_text: str, style: AllowedStyle) -> str:
        style = style.strip()
        if style not in {"APA", "MLA", "IEEE", "Chicago", "Harvard"}:
            raise ValueError("Unsupported citation style")

        reference_text = reference_text.strip()
        if not reference_text:
            raise ValueError("Reference text cannot be empty")

        chain = self.prompt | self.llm
        response = chain.invoke({"style": style, "reference": reference_text})
        content = getattr(response, "content", response)
        formatted = str(content).strip()

        if not formatted:
            raise RuntimeError("Formatter returned empty response")

        return formatted


