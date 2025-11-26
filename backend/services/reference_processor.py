"""
Reference processing service using LangChain and MistralAI
"""

from langchain_core.prompts import PromptTemplate
from typing import List, Dict
import json
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ReferenceProcessor:
    """Process references using MistralAI via LangChain"""
    
    def __init__(self):
        # Initialize MistralAI LLM using API key from .env file
        mistral_api_key = os.getenv("MISTRAL_API_KEY", "").strip()
        
        if not mistral_api_key:
            raise ValueError(
                "MISTRAL_API_KEY not found. "
                "Please create a .env file in the backend directory with: MISTRAL_API_KEY=your-api-key"
            )
        
        try:
            # Use MistralAI API directly (using langchain-mistralai)
            from langchain_mistralai import ChatMistralAI
            self.llm = ChatMistralAI(
                mistral_api_key=mistral_api_key,
                model="mistral-small",
                temperature=0.1
            )
            print("Using MistralAI API with mistral-small model")
        except ImportError:
            raise ImportError(
                "langchain-mistralai package is required. "
                "Install it with: pip install langchain-mistralai"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize MistralAI API: {str(e)}. "
                "Please check your MISTRAL_API_KEY and network connection."
            )
        
        self.prompt_template = PromptTemplate(
            input_variables=["references_text"],
            template="""You are 'ReferenceVerificationAgent', working inside a LangChain + MistralAI RAG pipeline.

Given RAG-retrieved text (References section), extract reference entries and return ONLY valid JSON array:

[
  {{
    "original_reference": "<full reference text>",
    "urls": ["<url1>", "<url2>"],
    "type": "Research Paper | News Article | YouTube Video | General Web Reference | Unknown"
  }}
]

Rules:
- Do NOT hallucinate URLs. Only extract URLs that actually exist in the text.
- Return ONLY valid JSON. No comments, explanations, or text outside JSON.
- Preserve exact reference text as it appears.
- Classify using domain detection:
  * DOI/arxiv/ieee/acm/springer/nature/wiley → "Research Paper"
  * bbc/cnn/nytimes/guardian/reuters/timesofindia → "News Article"
  * youtube.com/youtu.be → "YouTube Video"
  * Other URLs → "General Web Reference"
  * No URL found → "Unknown"
- Extract each distinct reference entry separately.
- Do not merge separate references.

References text:
{references_text}

Return ONLY the JSON array:"""
        )
    
    def process_references(self, references_text: str) -> List[Dict]:
        """
        Process references section and extract structured data.
        
        Args:
            references_text: Text containing references
            
        Returns:
            List of reference dictionaries
        """
        try:
            references_text = self._normalize_reference_section(references_text)

            # Use LCEL (LangChain Expression Language) for LangChain 1.0+
            chain = self.prompt_template | self.llm
            response = chain.invoke({"references_text": references_text})
            
            # Extract content if it's a message object
            if hasattr(response, 'content'):
                response = response.content
            elif isinstance(response, str):
                response = response
            else:
                # Try to convert to string
                response = str(response)
            
            # Clean response - extract JSON from response
            json_str = self._extract_json(str(response))
            
            # Parse JSON
            references = json.loads(json_str)
            
            # Validate and clean references
            validated_references = []
            for ref in references:
                if isinstance(ref, dict) and "original_reference" in ref:
                    validated_ref = {
                        "original_reference": ref.get("original_reference", "").strip(),
                        "type": ref.get("type", "Unknown"),
                    }

                    # Normalize URLs and capture metadata
                    raw_urls = ref.get("urls", [])
                    if not isinstance(raw_urls, list):
                        raw_urls = []

                    normalized_urls = []
                    url_details = []
                    for url in raw_urls:
                        if not isinstance(url, str):
                            continue
                        cleaned = (
                            url.replace(' ', '')
                               .replace('\n', '')
                               .replace('\r', '')
                               .replace('\t', '')
                               .rstrip('.,;:')
                        )
                        if cleaned.startswith(('http://', 'https://')):
                            normalized_urls.append(cleaned)
                            url_details.append({"url": cleaned, "source": "pdf"})

                    validated_ref["urls"] = normalized_urls
                    validated_ref["url_details"] = url_details

                    validated_references.append(validated_ref)

            if not validated_references:
                # Fallback to regex-based extraction when LLM returns nothing
                trimmed_text = self._trim_to_reference_start(references_text)
                return self._fallback_extraction(trimmed_text)

            return validated_references
        
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            # Fallback: try to extract references manually
            return self._fallback_extraction(references_text)
        except Exception as e:
            print(f"Error processing references: {str(e)}")
            # Fallback: try to extract references manually
            trimmed_text = self._trim_to_reference_start(references_text)
            return self._fallback_extraction(trimmed_text)
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response"""
        # Try to find JSON array
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text.strip()
    
    def _fallback_extraction(self, text: str) -> List[Dict]:
        """Fallback method to extract references if LLM fails"""
        references = []
        
        # Split by common reference patterns
        ref_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'^\d+\.',   # 1., 2., etc.
            r'\(\d+\)',  # (1), (2), etc.
        ]
        
        lines = text.split('\n')
        current_ref = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_ref:
                    ref_text = ' '.join(current_ref)
                    urls = self._extract_urls(ref_text)
                    ref_type = self._classify_reference(urls)
                    references.append({
                        "original_reference": ref_text,
                        "urls": urls,
                        "url_details": [{"url": url, "source": "pdf"} for url in urls],
                        "type": ref_type
                    })
                    current_ref = []
                continue
            
            # Check if new reference starts
            is_new_ref = any(re.match(pattern, line) for pattern in ref_patterns)
            
            if is_new_ref and current_ref:
                # Save previous reference
                ref_text = ' '.join(current_ref)
                urls = self._extract_urls(ref_text)
                ref_type = self._classify_reference(urls)
                references.append({
                    "original_reference": ref_text,
                    "urls": urls,
                    "url_details": [{"url": url, "source": "pdf"} for url in urls],
                    "type": ref_type
                })
                current_ref = [line]
            else:
                current_ref.append(line)
        
        # Add last reference
        if current_ref:
            ref_text = ' '.join(current_ref)
            urls = self._extract_urls(ref_text)
            ref_type = self._classify_reference(urls)
            references.append({
                "original_reference": ref_text,
                "urls": urls,
                "url_details": [{"url": url, "source": "pdf"} for url in urls],
                "type": ref_type
            })
        
        return references

    def _normalize_reference_section(self, text: str) -> str:
        """Ensure the references text starts near the first numbered entry."""
        trimmed = self._trim_to_reference_start(text)
        return trimmed

    def _trim_to_reference_start(self, text: str) -> str:
        """Trim any leading narrative content before the first reference marker."""
        lines = text.splitlines()
        start_index = 0
        patterns = [
            re.compile(r"^\s*\[\d+\]"),
            re.compile(r"^\s*\d+\."),
            re.compile(r"^\s*\(\d+\)"),
        ]

        for idx, line in enumerate(lines):
            clean = line.strip()
            if not clean:
                continue
            if any(pattern.match(clean) for pattern in patterns):
                start_index = idx
                break

        trimmed_lines = lines[start_index:]
        return "\n".join(trimmed_lines).strip()
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        # First, try to find URLs that might be broken across lines (with spaces/hyphens)
        # Pattern to match URLs that may have spaces or line breaks
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:\s+[^\s<>"{}|\\^`\[\]]+)*|doi\.org/[^\s<>"{}|\\^`\[\]]+(?:\s+[^\s<>"{}|\\^`\[\]]+)*|doi:[^\s<>"{}|\\^`\[\]]+(?:\s+[^\s<>"{}|\\^`\[\]]+)*'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        
        # Normalize URLs - remove spaces and fix common issues
        normalized = []
        for url in urls:
            # Remove all spaces from the URL
            url = url.replace(' ', '')
            url = url.replace('\n', '')
            url = url.replace('\r', '')
            url = url.replace('\t', '')
            
            # Handle DOI formats
            if url.lower().startswith('doi:'):
                url = f"https://doi.org/{url[4:].strip()}"
            elif url.lower().startswith('doi.org/'):
                url = f"https://{url}"
            
            # Remove trailing punctuation
            url = url.rstrip('.,;:')
            
            # Only add if it's a valid-looking URL
            if url.startswith(('http://', 'https://')):
                normalized.append(url)
        
        return list(set(normalized))
    
    def _classify_reference(self, urls: List[str]) -> str:
        """Classify reference based on URLs"""
        if not urls:
            return "Unknown"
        
        for url in urls:
            url_lower = url.lower()
            
            # Research Paper
            research_domains = ['doi.org', 'arxiv.org', 'ieee.org', 'acm.org', 
                              'springer.com', 'nature.com', 'wiley.com', 
                              'sciencedirect.com', 'pubmed.ncbi.nlm.nih.gov']
            if any(domain in url_lower for domain in research_domains):
                return "Research Paper"
            
            # News Article
            news_domains = ['bbc.com', 'bbc.co.uk', 'cnn.com', 'nytimes.com',
                          'theguardian.com', 'reuters.com', 'timesofindia.indiatimes.com',
                          'indianexpress.com', 'thehindu.com']
            if any(domain in url_lower for domain in news_domains):
                return "News Article"
            
            # YouTube
            if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                return "YouTube Video"
        
        return "General Web Reference"

