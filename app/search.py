from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import aiohttp
import os
import logging
from bs4 import BeautifulSoup
from fastapi import HTTPException
from .config import Settings

logger = logging.getLogger(__name__)

class SearchResult:
    def __init__(self, title: str, link: str, snippet: Optional[str] = None, 
                 source: Optional[str] = None, position: Optional[int] = None,
                 additional_data: Optional[dict] = None):
        self.title = title
        self.link = link
        self.snippet = snippet
        self.source = source
        self.position = position
        self.additional_data = additional_data or {}
    
    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "source": self.source,
            "position": self.position,
            "additional_data": self.additional_data
        }

class SearchEngine(ABC):
    """Base class for search engine implementations"""
    
    @abstractmethod
    async def search(self, query: str, num_results: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Perform a search and return results"""
        pass

class GoogleSearch(SearchEngine):
    """Google search implementation using Google Custom Search API"""
    
    def __init__(self, api_key: str, cx: str):
        self.api_key = api_key
        self.cx = cx
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    async def search(self, query: str, num_results: int = 10, 
                    language: str = "en", country: str = "us", 
                    safe_search: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Google using the Custom Search API
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10 per request)
            language: Language code (e.g., 'en', 'es')
            country: Country code (e.g., 'us', 'uk')
            safe_search: Whether to enable safe search
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            List of search results
        """
        if not self.api_key or not self.cx:
            raise HTTPException(status_code=500, detail="Google API key or CX not configured")
        
        # Google API allows max 10 results per request, so we need to make multiple requests
        results = []
        remaining = min(num_results, 100)  # Limit to 100 results max
        start_index = 1
        
        # Prepare parameters
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "hl": language,
            "gl": country,
            "safe": "active" if safe_search else "off",
        }
        
        # Add any additional parameters
        params.update(kwargs)
        
        async with aiohttp.ClientSession() as session:
            while remaining > 0:
                # Number of results to request in this batch (max 10)
                current_num = min(remaining, 10)
                
                # Set the start index and number of results
                params["start"] = start_index
                params["num"] = current_num
                
                try:
                    async with session.get(self.base_url, params=params) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"Google API error: {response.status} - {error_text}")
                            raise HTTPException(
                                status_code=response.status,
                                detail=f"Google API error: {error_text}"
                            )
                        
                        data = await response.json()
                        
                        # Process results
                        if "items" in data:
                            for i, item in enumerate(data["items"]):
                                position = start_index + i - 1
                                result = SearchResult(
                                    title=item.get("title", ""),
                                    link=item.get("link", ""),
                                    snippet=item.get("snippet", ""),
                                    source="google",
                                    position=position,
                                    additional_data={
                                        "displayLink": item.get("displayLink"),
                                        "formattedUrl": item.get("formattedUrl"),
                                        "htmlSnippet": item.get("htmlSnippet"),
                                        "htmlTitle": item.get("htmlTitle"),
                                        "kind": item.get("kind"),
                                        "mime": item.get("mime")
                                    }
                                )
                                results.append(result.to_dict())
                            
                            # Update for next iteration
                            start_index += len(data["items"])
                            remaining -= len(data["items"])
                            
                            # If fewer results returned than requested, we're done
                            if len(data["items"]) < current_num:
                                break
                        else:
                            # No more results
                            break
                            
                except Exception as e:
                    logger.error(f"Error in Google search: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Google search error: {str(e)}")
        
        return results[:num_results]  # Ensure we don't return more than requested

class DuckDuckGoSearch(SearchEngine):
    """
    DuckDuckGo search implementation using HTML scraping
    
    Note: This is a basic implementation and might break if DuckDuckGo changes their HTML structure.
    Using their API would be preferred if available.
    """
    
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def search(self, query: str, num_results: int = 10, 
                    language: str = "en", country: str = "us", 
                    safe_search: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo by scraping their HTML search page
        
        Args:
            query: Search query string
            num_results: Number of results to return
            language: Language code (e.g., 'en', 'es')
            country: Country code (e.g., 'us', 'uk')
            safe_search: Whether to enable safe search
            **kwargs: Additional parameters
            
        Returns:
            List of search results
        """
        params = {
            "q": query,
            "kl": f"{country}-{language}"
        }
        
        if safe_search:
            params["kp"] = "1"
        
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, data=params, headers=self.headers) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"DuckDuckGo search failed with status {response.status}"
                        )
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Extract search results
                    result_elements = soup.select(".result")
                    
                    for i, result in enumerate(result_elements[:num_results]):
                        # Extract data from the result
                        title_element = result.select_one(".result__title")
                        title = title_element.get_text(strip=True) if title_element else "No title"
                        
                        link_element = result.select_one(".result__url")
                        # The actual link is in the href of the <a> inside title
                        a_element = title_element.select_one("a") if title_element else None
                        link = a_element["href"] if a_element and "href" in a_element.attrs else ""
                        
                        snippet_element = result.select_one(".result__snippet")
                        snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                        
                        result_obj = SearchResult(
                            title=title,
                            link=link,
                            snippet=snippet,
                            source="duckduckgo",
                            position=i + 1
                        )
                        
                        results.append(result_obj.to_dict())
                        
        except Exception as e:
            logger.error(f"Error in DuckDuckGo search: {str(e)}")
            raise HTTPException(status_code=500, detail=f"DuckDuckGo search error: {str(e)}")
        
        return results

class BingSearch(SearchEngine):
    """Bing search implementation using Bing Search API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {"Ocp-Apim-Subscription-Key": api_key}
    
    async def search(self, query: str, num_results: int = 10, 
                    language: str = "en", country: str = "us", 
                    safe_search: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Search Bing using the Bing Search API
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 50 per request)
            language: Language code (e.g., 'en', 'es')
            country: Country code (e.g., 'us', 'uk')
            safe_search: Whether to enable safe search
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            List of search results
        """
        if not self.api_key:
            raise HTTPException(status_code=500, detail="Bing API key not configured")
        
        # Prepare parameters
        params = {
            "q": query,
            "count": min(num_results, 50),  # Bing allows up to 50 results per request
            "setLang": language,
            "cc": country,
            "safeSearch": "Strict" if safe_search else "Off",
        }
        
        # Add any additional parameters
        params.update(kwargs)
        
        results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, headers=self.headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Bing API error: {response.status} - {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Bing API error: {error_text}"
                        )
                    
                    data = await response.json()
                    
                    # Process results
                    if "webPages" in data and "value" in data["webPages"]:
                        for i, item in enumerate(data["webPages"]["value"][:num_results]):
                            result = SearchResult(
                                title=item.get("name", ""),
                                link=item.get("url", ""),
                                snippet=item.get("snippet", ""),
                                source="bing",
                                position=i + 1,
                                additional_data={
                                    "id": item.get("id"),
                                    "displayUrl": item.get("displayUrl"),
                                    "dateLastCrawled": item.get("dateLastCrawled")
                                }
                            )
                            results.append(result.to_dict())
            
        except Exception as e:
            logger.error(f"Error in Bing search: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Bing search error: {str(e)}")
        
        return results

def get_search_engine(engine_name: str, settings: Settings) -> SearchEngine:
    """Factory function to get the appropriate search engine"""
    engine_name = engine_name.lower()
    
    if engine_name == "google":
        return GoogleSearch(api_key=settings.google_api_key, cx=settings.google_cx)
    elif engine_name == "duckduckgo":
        return DuckDuckGoSearch()
    elif engine_name == "bing":
        return BingSearch(api_key=settings.bing_api_key)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported search engine: {engine_name}")