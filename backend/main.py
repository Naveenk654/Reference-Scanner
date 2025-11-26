"""
FastAPI backend for RefCheck - Reference Verification System
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os
import tempfile
import shutil
from dotenv import load_dotenv
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("refcheck")

# Load environment variables
load_dotenv()

# Get port from environment variable or use default
PORT = int(os.getenv("PORT", 8002))

from services.pdf_extractor import PDFExtractor
from services.rag_service import RAGService
from services.reference_processor import ReferenceProcessor
from services.url_checker import URLChecker
from services.reference_linker import ReferenceLinker
from services.citation_formatter import CitationFormatter
from services.research_chatbot import ResearchChatbot
from services.web_search import WebSearchService

app = FastAPI(title="RefCheck API", version="1.0.0")

# CORS configuration
# Get allowed origins from environment variable or use defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
default_origins = [
    "http://localhost:5173",
    "http://localhost:5174", 
    "http://localhost:3000", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174"
]
# Combine default origins with environment variable origins, filter out empty strings
all_origins = [origin.strip() for origin in default_origins + allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (with error handling)
try:
    pdf_extractor = PDFExtractor()
    rag_service = RAGService()
    reference_processor = ReferenceProcessor()
    reference_linker = ReferenceLinker()
    citation_formatter = CitationFormatter()
    chatbot_service = ResearchChatbot()
    try:
        web_search_service: Optional[WebSearchService] = WebSearchService()
        logger.info("Web search service initialized with Tavily")
    except Exception as search_exc:
        web_search_service = None
        logger.warning("Web search disabled: %s", search_exc)
    url_checker = URLChecker()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

class URLDetail(BaseModel):
    url: str
    source: str


class ReferenceResponse(BaseModel):
    original_reference: str
    urls: List[str]
    url_details: List[URLDetail]
    type: str
    status: str

class ProcessResponse(BaseModel):
    success: bool
    references: List[ReferenceResponse]
    message: Optional[str] = None


class FormatRequest(BaseModel):
    style: str
    reference: str


class FormatResponse(BaseModel):
    success: bool
    formatted_reference: str


class ConversationMessage(BaseModel):
    role: str
    content: str


class ChatbotRequest(BaseModel):
    question: str
    reference_text: Optional[str] = None
    mode: Optional[str] = "general"
    history: Optional[List[ConversationMessage]] = None


class ChatbotResponse(BaseModel):
    success: bool
    answer: str

def classify_reference_by_urls(urls: List[str]) -> str:
    """Classify reference type purely from URL domains."""
    if not urls:
        return "Unknown"

    research_domains = [
        "doi.org",
        "arxiv.org",
        "ieee.org",
        "acm.org",
        "springer.com",
        "nature.com",
        "wiley.com",
        "sciencedirect.com",
        "pubmed.ncbi.nlm.nih.gov",
    ]
    news_domains = [
        "bbc.com",
        "bbc.co.uk",
        "cnn.com",
        "nytimes.com",
        "theguardian.com",
        "reuters.com",
        "timesofindia.indiatimes.com",
        "indianexpress.com",
        "thehindu.com",
    ]

    for url in urls:
        url_lower = url.lower()
        if any(domain in url_lower for domain in research_domains):
            return "Research Paper"
        if any(domain in url_lower for domain in news_domains):
            return "News Article"
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "YouTube Video"

    return "General Web Reference"


def should_use_web_search(question: str) -> bool:
    """Determine if the query benefits from live web search context."""
    if not question:
        return False

    lowered = question.lower()
    trigger_keywords = [
        "latest",
        "recent",
        "update",
        "link",
        "url",
        "source",
        "news",
        "article",
        "paper",
        "where can i find",
        "provide link",
    ]
    return any(keyword in lowered for keyword in trigger_keywords)


def format_web_results(results: List[Dict[str, str]]) -> str:
    if not results:
        return ""

    lines = []
    for idx, item in enumerate(results, start=1):
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        snippet = item.get("content", "")
        lines.append(f"[{idx}] {title}\nURL: {url}\nSnippet: {snippet}")
    return "\n\n".join(lines)


@app.get("/")
async def root():
    return {"status": "healthy", "service": "RefCheck API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

PRIORITY = ["Broken", "Timeout", "Not Working", "Working"]

@app.post("/upload_pdf", response_model=ProcessResponse)
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        try:
            logger.info("Extracting text from PDF...")
            pdf_text = pdf_extractor.extract_text(tmp_path)

            if not pdf_text:
                raise HTTPException(status_code=400, detail="Could not extract text from PDF")

            logger.info("Retrieving References section using RAG...")
            references_section = rag_service.retrieve_references_section(pdf_text)

            if not references_section:
                # Provide more helpful error message
                pdf_length = len(pdf_text)
                logger.warning(f"References section not found. PDF text length: {pdf_length} characters")
                raise HTTPException(
                    status_code=400, 
                    detail=f"References section not found in PDF. The PDF may not have a clearly marked References/Bibliography section, or it may be formatted differently. PDF contains {pdf_length} characters of text."
                )

            logger.info("Processing references with MistralAI...")
            references = reference_processor.process_references(references_section)

            # Fill in missing URLs via search heuristics
            references = reference_linker.enrich(references)

            if not references:
                raise HTTPException(status_code=400, detail="No references detected")

            logger.info("Checking URL statuses...")
            final_references = []

            for ref in references:
                statuses = []
                for url in ref.get("urls", []):
                    statuses.append(url_checker.check_url(url))

                overall_status = "Unknown"
                if statuses:
                    sorted_status = sorted(statuses, key=lambda s: PRIORITY.index(s))
                    overall_status = sorted_status[0]

                url_details = ref.get("url_details")
                if not url_details and ref.get("urls"):
                    url_details = [{"url": url, "source": "unknown"} for url in ref["urls"]]

                ref_type = ref.get("type") or "Unknown"
                if ref_type == "Unknown" and ref.get("urls"):
                    ref_type = classify_reference_by_urls(ref["urls"])

                final_references.append({
                    "original_reference": ref["original_reference"],
                    "urls": ref["urls"],
                    "url_details": url_details or [],
                    "type": ref_type,
                    "status": overall_status
                })

            return ProcessResponse(
                success=True,
                references=final_references,
                message=f"Successfully processed {len(final_references)} references"
            )

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Traceback: {error_details}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing PDF: {str(e)}. Check server logs for details."
        )


@app.post("/format_reference", response_model=FormatResponse)
async def format_reference_endpoint(payload: FormatRequest):
    style = payload.style.strip()
    reference_text = payload.reference.strip()

    if not style or not reference_text:
        raise HTTPException(status_code=400, detail="STYLE and REFERENCE are required")

    try:
        formatted = citation_formatter.format_reference(reference_text, style)
        return FormatResponse(success=True, formatted_reference=formatted)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Error formatting reference: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to format reference: {str(exc)}",
        )


@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_endpoint(payload: ChatbotRequest):
    if not payload.question:
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        reference_context = (payload.reference_text or "").strip()

        if web_search_service and should_use_web_search(payload.question):
            logger.info("Web search triggered for chatbot question: %s", payload.question)
            search_results = web_search_service.search(payload.question)
            logger.info("Web search returned %d results", len(search_results))
            web_context = format_web_results(search_results)
            if web_context:
                reference_context = (
                    f"{reference_context}\n\nWeb search context:\n{web_context}"
                ).strip()

        history_payload = []
        if payload.history:
            for msg in payload.history:
                history_payload.append(msg.model_dump())

        answer = chatbot_service.chat(
            question=payload.question,
            reference_text=reference_context,
            mode=payload.mode or "general",
            history=history_payload,
        )
        return ChatbotResponse(success=True, answer=answer)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Chatbot error: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate chatbot response",
        )


if __name__ == "__main__":
    logger.info(f"Starting RefCheck backend server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
