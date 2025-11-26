"""
URL status checking service
"""

import requests
from typing import Literal
import time


class URLChecker:
    """Check URL status (Working, Not Working, Timeout, Broken)"""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize URL checker.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_url(self, url: str) -> Literal["Working", "Not Working", "Timeout", "Broken"]:
        """
        Check if a URL is working.
        
        Args:
            url: URL to check
            
        Returns:
            Status: "Working", "Not Working", "Timeout", or "Broken"
        """

        def _request(method: str):
            """Helper to execute HEAD/GET with shared error handling."""
            try:
                response = getattr(self.session, method)(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    stream=(method == "get")
                )
                status = response.status_code
                if method == "get":
                    response.close()
                return status
            except requests.exceptions.Timeout:
                return "Timeout"
            except requests.exceptions.RequestException:
                return None

        try:
            # Normalize URL - remove spaces, newlines, and tabs
            url = url.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
            url = url.strip()
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            status_code = _request("head")
            if status_code == "Timeout":
                return "Timeout"
            
            # Some sites block HEAD or return 4xx, so fall back to GET
            if status_code is None or status_code >= 400:
                status_code = _request("get")
                if status_code == "Timeout":
                    return "Timeout"
                if status_code is None:
                    return "Broken"
            
            # Treat auth-required responses as reachable
            if status_code in (401, 403, 405, 429):
                return "Working"
            if 200 <= status_code < 400:
                return "Working"
            if 400 <= status_code < 500:
                return "Broken"
            return "Not Working"
        
        except Exception as e:
            print(f"Error checking URL {url}: {str(e)}")
            return "Broken"

