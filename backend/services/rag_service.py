import os
import re
from typing import Optional, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from mistralai import Mistral


class MistralEmbeddingFunction:
    """A wrapper to make Mistral embeddings compatible with LangChain."""
    
    def __init__(self):
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    def __call__(self, texts: List[str]):
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embeddings.create(
            model="mistral-embed",
            input=texts
        )

        return [item.embedding for item in response.data]


class RAGService:
    def __init__(self):
        self.chunk_size = 1200
        self.chunk_overlap = 150
        self.embedder = MistralEmbeddingFunction()

    def _extract_references_regex(self, text: str):
        headings = ["REFERENCES", "REFERENCE", "BIBLIOGRAPHY", "WORKS CITED"]
        end_markers = [
            "APPENDIX",
            "ANNEX",
            "ACKNOWLEDGMENTS",
            "ACKNOWLEDGEMENTS",
            "AUTHOR",
            "BIOGRAPHY",
            "ABOUT",
            "SUPPLEMENTARY",
        ]

        for heading in headings:
            pattern = re.compile(
                rf"(?:^|\n)\s*{heading}\s*[\r\n]+([\s\S]+?)(?:\n\s*(?:{'|'.join(end_markers)})\b|$)",
                re.IGNORECASE,
            )
            match = pattern.search(text)
            if match:
                extracted = match.group(1).strip()
                if len(extracted) > 50:
                    return extracted

        return None

    def retrieve_references_section(self, full_text: str):
        # STEP 1 — Regex first
        refs = self._extract_references_regex(full_text)
        if refs:
            print("✔ REGEX found reference section.")
            return refs

        print("⚠ REGEX failed → trying RAG fallback...")

        # STEP 2 — RAG fallback
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )

            docs = splitter.create_documents([full_text])

            # Create vector store with Mistral embeddings
            vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embedder,
                collection_name="refcheck_temp"
            )

            retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

            query = "Return only the References or Bibliography section of this research paper."

            # Now retrieval works normally
            results = retriever.get_relevant_documents(query)

            if not results:
                return None

            combined = "\n\n".join([doc.page_content for doc in results])

            if len(combined.strip()) < 50:
                return None

            return combined

        except Exception as e:
            print("❌ RAG fallback error:", str(e))
            return None
