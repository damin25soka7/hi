"""
Enhanced Web Crawler with advanced features from mcp-searxng-enhanced
Includes:
- Category-aware search (images, videos, files, map, social media)
- PDF reading with Markdown conversion
- Caching with TTL and validation
- Rate limiting
- Reddit URL conversion
- Enhanced content extraction with Trafilatura
"""

import asyncio
import httpx
import time
import re
import unicodedata
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone
from cachetools import TTLCache
from dateutil import parser as date_parser
import trafilatura
import filetype
import pymupdf
import pymupdf4llm
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Domain-based rate limiting for web requests."""
    
    def __init__(self, requests_per_minute: int = 10, timeout_seconds: int = 60):
        self.requests_per_minute = requests_per_minute
        self.timeout_seconds = timeout_seconds
        self.domain_requests = {}
        
    def can_request(self, url: str) -> bool:
        """Check if a request to the given URL is allowed under rate limits."""
        domain = urlparse(url).netloc
        if not domain:
            return True
            
        current_time = time.time()
        
        if domain not in self.domain_requests:
            self.domain_requests[domain] = []
            
        # Clean up old requests
        self.domain_requests[domain] = [
            timestamp for timestamp in self.domain_requests[domain]
            if current_time - timestamp < self.timeout_seconds
        ]
        
        # Check if we're over the limit
        if len(self.domain_requests[domain]) >= self.requests_per_minute:
            return False
            
        # Add current request timestamp
        self.domain_requests[domain].append(current_time)
        return True
        
    def get_remaining_time(self, url: str) -> float:
        """Get the remaining time in seconds before a request can be made."""
        domain = urlparse(url).netloc
        if not domain or domain not in self.domain_requests:
            return 0
            
        current_time = time.time()
        timestamps = self.domain_requests[domain]
        
        timestamps = [t for t in timestamps if current_time - t < self.timeout_seconds]
        
        if len(timestamps) < self.requests_per_minute:
            return 0
            
        oldest = min(timestamps)
        return max(0, oldest + self.timeout_seconds - current_time)


class CacheValidator:
    """Validates cached web content freshness."""
    
    @staticmethod
    def is_valid(cached_result: Dict[str, Any], max_age_minutes: int = 30) -> bool:
        """Check if a cached result is still valid."""
        if not cached_result:
            return False
            
        if "date_accessed" not in cached_result:
            return False
            
        try:
            date_accessed = date_parser.parse(cached_result["date_accessed"])
            now = datetime.now(timezone.utc)
            age_td = now - date_accessed
            return age_td.total_seconds() < (max_age_minutes * 60)
        except (ValueError, TypeError):
            return False


class HelperFunctions:
    """Helper utilities for content processing."""
    
    @staticmethod
    def remove_emojis(text: str) -> str:
        """Remove emoji characters from text."""
        return "".join(c for c in text if not unicodedata.category(c).startswith("So"))
    
    @staticmethod
    def format_text_with_trafilatura(html_content: str, timeout: int = 15) -> str:
        """Extract clean text from HTML using Trafilatura."""
        extracted_text = trafilatura.extract(
            html_content,
            favor_readability=True,
            include_comments=False,
            include_tables=True,
            timeout=timeout
        )
        
        if not extracted_text:
            soup = BeautifulSoup(html_content, "html.parser")
            extracted_text = soup.get_text(separator="\n", strip=True)
            logger.warning("Trafilatura failed/timed out, falling back to basic text extraction.")
        
        lines = [unicodedata.normalize("NFKC", line).strip() for line in extracted_text.splitlines()]
        cleaned_lines = [re.sub(r'\s{2,}', ' ', line) for line in lines if line]
        formatted_text = "\n".join(cleaned_lines)
        
        return HelperFunctions.remove_emojis(formatted_text).strip()
    
    @staticmethod
    def truncate_to_n_words(text: str, word_limit: int) -> str:
        """Truncate text to a specified number of words."""
        tokens = text.split()
        if len(tokens) <= word_limit:
            return text
        return " ".join(tokens[:word_limit]) + "..."
    
    @staticmethod
    def generate_excerpt(content: str, max_length: int = 200) -> str:
        """Generate a short excerpt from content."""
        lines = content.splitlines()
        excerpt = ""
        for line in lines:
            if len(excerpt) + len(line) + 1 < max_length:
                excerpt += line + "\n"
            else:
                remaining_len = max_length - len(excerpt) - 4
                if remaining_len > 0:
                    excerpt += line[:remaining_len] + " ..."
                break
        return excerpt.strip() if excerpt else content[:max_length] + "..."
    
    @staticmethod
    def modify_reddit_url(url: str) -> str:
        """Convert Reddit URLs to old.reddit.com for better scraping."""
        match = re.match(r"^(https?://)(www\.)?(reddit\.com)(.*)$", url, re.IGNORECASE)
        if match:
            protocol = match.group(1)
            path_and_query = match.group(4)
            return f"{protocol}old.reddit.com{path_and_query}"
        return url


class EnhancedWebCrawler:
    """
    Enhanced Web Crawler with advanced features:
    - Category-aware search
    - PDF reading with Markdown conversion
    - Caching with TTL
    - Rate limiting
    - Enhanced content extraction
    """
    
    def __init__(
        self,
        searxng_url: str = "http://localhost:32768/search",
        cache_maxsize: int = 100,
        cache_ttl_minutes: int = 5,
        cache_max_age_minutes: int = 30,
        rate_limit_requests_per_minute: int = 10,
        rate_limit_timeout_seconds: int = 60,
        mock_mode: bool = False
    ):
        self.searxng_url = searxng_url
        self.mock_mode = mock_mode
        self.cache_max_age_minutes = cache_max_age_minutes
        
        # Initialize cache
        self.website_cache = TTLCache(
            maxsize=cache_maxsize,
            ttl=cache_ttl_minutes * 60
        )
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=rate_limit_requests_per_minute,
            timeout_seconds=rate_limit_timeout_seconds
        )
        
        logger.info(f"EnhancedWebCrawler initialized: {self.searxng_url}")
        logger.info(f"Cache: maxsize={cache_maxsize}, ttl={cache_ttl_minutes}min, max_age={cache_max_age_minutes}min")
        logger.info(f"Rate limit: {rate_limit_requests_per_minute} req/min per domain")
    
    async def search_with_category(
        self,
        query: str,
        limit: int = 10,
        category: str = "general",
        language: str = "auto",
        time_range: str = "",
        safe_search: int = 1,
        engines: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search with category support (general, images, videos, files, map, social media).
        Returns structured data appropriate for the category.
        """
        try:
            params = {
                "q": query,
                "format": "json",
                "pageno": 1,
                "categories": category.lower(),
                "safesearch": safe_search
            }
            
            if engines:
                params["engines"] = engines
            
            if language != "auto":
                params["language"] = language
            
            if time_range:
                params["time_range"] = time_range
            
            logger.info(f"🔍 Category Search: '{query}' in '{category}'")
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(
                    self.searxng_url,
                    params=params,
                    headers={"User-Agent": "MCP-Enhanced-Search-Bot/2.0"}
                )
                
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                
                logger.info(f"✅ Got {len(results)} raw results")
                
                # Process results based on category
                if category.lower() == "images":
                    return await self._process_image_results(results, limit)
                elif category.lower() == "videos":
                    return await self._process_video_results(results, limit)
                elif category.lower() == "files":
                    return await self._process_file_results(results, limit)
                elif category.lower() == "map":
                    return await self._process_map_results(results, limit)
                elif category.lower() == "social media":
                    return await self._process_social_results(results, limit)
                else:
                    # General category - scrape content
                    return await self._process_general_results(results, limit)
        
        except Exception as e:
            logger.error(f" Search error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "category": category,
                "results": []
            }
    
    async def _process_image_results(self, results: List[Dict], limit: int) -> Dict[str, Any]:
        """Process image search results."""
        processed = []
        for result in results[:limit]:
            processed.append({
                "type": "image",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "img_src": result.get("img_src", ""),
                "thumbnail": result.get("thumbnail_src", "")
            })
        
        return {
            "success": True,
            "category": "images",
            "count": len(processed),
            "results": processed
        }
    
    async def _process_video_results(self, results: List[Dict], limit: int) -> Dict[str, Any]:
        """Process video search results."""
        processed = []
        for result in results[:limit]:
            processed.append({
                "type": "video",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "iframe_src": result.get("iframe_src", ""),
                "thumbnail": result.get("thumbnail", "")
            })
        
        return {
            "success": True,
            "category": "videos",
            "count": len(processed),
            "results": processed
        }
    
    async def _process_file_results(self, results: List[Dict], limit: int) -> Dict[str, Any]:
        """Process file search results."""
        processed = []
        for result in results[:limit]:
            processed.append({
                "type": "file",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "format": result.get("format", ""),
                "size": result.get("size", "")
            })
        
        return {
            "success": True,
            "category": "files",
            "count": len(processed),
            "results": processed
        }
    
    async def _process_map_results(self, results: List[Dict], limit: int) -> Dict[str, Any]:
        """Process map/location search results."""
        processed = []
        for result in results[:limit]:
            processed.append({
                "type": "map",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "address": result.get("address", ""),
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "content": result.get("content", "")
            })
        
        return {
            "success": True,
            "category": "map",
            "count": len(processed),
            "results": processed
        }
    
    async def _process_social_results(self, results: List[Dict], limit: int) -> Dict[str, Any]:
        """Process social media search results."""
        processed = []
        for result in results[:limit]:
            processed.append({
                "type": "social",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")
            })
        
        return {
            "success": True,
            "category": "social media",
            "count": len(processed),
            "results": processed
        }
    
    async def _process_general_results(self, results: List[Dict], limit: int) -> Dict[str, Any]:
        """Process general web search results with content scraping."""
        processed = []
        
        for result in results[:limit]:
            url = result.get("url", "")
            if not url:
                continue
            
            # Check rate limit
            if not self.rate_limiter.can_request(url):
                logger.warning(f" Rate limit exceeded for {urlparse(url).netloc}")
                continue
            
            # Try to scrape content
            content_data = await self.fetch_webpage_enhanced(url, max_length=20000)
            
            if content_data.get("success"):
                processed.append({
                    "type": "webpage",
                    "title": content_data.get("title", result.get("title", "")),
                    "url": url,
                    "content": content_data.get("content", ""),
                    "excerpt": content_data.get("excerpt", ""),
                    "snippet": result.get("content", ""),
                    "date_accessed": content_data.get("date_accessed", "")
                })
            else:
                processed.append({
                    "type": "webpage",
                    "title": result.get("title", ""),
                    "url": url,
                    "snippet": result.get("content", ""),
                    "error": content_data.get("error", "Failed to fetch")
                })
        
        return {
            "success": True,
            "category": "general",
            "count": len(processed),
            "results": processed
        }
    
    async def fetch_webpage_enhanced(
        self,
        url: str,
        max_length: int = 10000,
        timeout: int = 30,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch webpage with enhanced features:
        - Caching with TTL and validation
        - PDF reading with Markdown conversion
        - Reddit URL conversion
        - Trafilatura content extraction
        """
        # Check cache first
        if use_cache and url in self.website_cache:
            cached = self.website_cache[url]
            if CacheValidator.is_valid(cached, self.cache_max_age_minutes):
                logger.info(f"💾 Cache hit: {url[:60]}")
                return cached
            else:
                logger.info(f"🔄 Cache stale: {url[:60]}")
        
        try:
            # Modify Reddit URLs
            url_to_fetch = HelperFunctions.modify_reddit_url(url)
            
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(
                    url_to_fetch,
                    headers={"User-Agent": "MCP-Enhanced-Crawler-Bot/2.0"}
                )
                response.raise_for_status()
                
                # Check if it's a PDF
                raw_content = response.content
                kind = filetype.guess(raw_content)
                
                if kind is not None and kind.mime == "application/pdf":
                    # Process PDF
                    logger.info(f"📄 PDF detected: {url[:60]}")
                    doc = pymupdf.open(stream=raw_content, filetype="pdf")
                    md_text = pymupdf4llm.to_markdown(doc)
                    
                    content = md_text
                    truncated_content = HelperFunctions.truncate_to_n_words(content, max_length // 5)
                    excerpt = HelperFunctions.generate_excerpt(content)
                    title = "PDF Document (converted to Markdown)"
                else:
                    # Process HTML
                    html_content = response.text
                    soup = BeautifulSoup(html_content, "html.parser")
                    
                    # Extract title
                    title_tag = soup.find('title')
                    title = title_tag.string if title_tag else "No title"
                    title = unicodedata.normalize("NFKC", title.strip())
                    title = HelperFunctions.remove_emojis(title)
                    
                    # Extract content
                    content = HelperFunctions.format_text_with_trafilatura(html_content, timeout=15)
                    truncated_content = HelperFunctions.truncate_to_n_words(content, max_length // 5)
                    excerpt = HelperFunctions.generate_excerpt(content)
                
                result = {
                    "success": True,
                    "url": url,
                    "title": title,
                    "content": truncated_content,
                    "excerpt": excerpt,
                    "date_accessed": datetime.now(timezone.utc).isoformat(),
                    "content_length": len(truncated_content)
                }
                
                # Cache the result
                if use_cache:
                    self.website_cache[url] = result
                
                return result
        
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "url": url,
                "error": f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "url": url,
                "error": f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def search_searxng(
        self, 
        query: str, 
        limit: int = 10,
        category: str = "general",
        language: str = "auto",
        time_range: str = "",
        safe_search: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Backward compatible search method.
        For general category, returns list of results.
        For other categories, returns structured data.
        """
        result = await self.search_with_category(
            query=query,
            limit=limit,
            category=category,
            language=language,
            time_range=time_range,
            safe_search=safe_search
        )
        
        if result.get("success"):
            return result.get("results", [])
        else:
            return []
    
    async def fetch_webpage(
        self, 
        url: str, 
        max_length: int = 10000,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Backward compatible fetch method."""
        return await self.fetch_webpage_enhanced(url, max_length, timeout)
