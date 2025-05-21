from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import time
from .search import GoogleSearch, DuckDuckGoSearch, BingSearch, get_search_engine
from .config import Settings, get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Web Search API",
    description="API service for performing web searches, similar to SerpAPI but self-hosted",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str
    engine: Optional[str] = "google"  # google, duckduckgo, bing
    num_results: Optional[int] = 10
    language: Optional[str] = "en"
    country: Optional[str] = "us"
    safe_search: Optional[bool] = True
    additional_params: Optional[Dict[str, Any]] = {}

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: Optional[str] = None
    source: Optional[str] = None
    position: Optional[int] = None
    additional_data: Optional[dict] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: Optional[int] = None
    search_time: float
    engine: str
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Web Search API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, settings: Settings = Depends(get_settings)):
    start_time = time.time()
    
    try:
        # Get the appropriate search engine based on the request
        search_engine = get_search_engine(request.engine, settings)
        
        # Perform the search
        search_results = await search_engine.search(
            query=request.query,
            num_results=request.num_results,
            language=request.language,
            country=request.country,
            safe_search=request.safe_search,
            **request.additional_params
        )
        
        # Calculate search time
        search_time = time.time() - start_time
        
        # Create and return response
        response = SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time=search_time,
            engine=request.engine
        )
        
        logger.info(f"Search completed: '{request.query}' with {len(search_results)} results in {search_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        search_time = time.time() - start_time
        
        # Return error response
        return SearchResponse(
            query=request.query,
            results=[],
            total_results=0,
            search_time=search_time,
            engine=request.engine,
            error=str(e)
        )

@app.get("/search", response_model=SearchResponse)
async def search_get(
    query: str = Query(..., description="Search query"),
    engine: str = Query("google", description="Search engine to use (google, duckduckgo, bing)"),
    num_results: int = Query(10, description="Number of results to return"),
    language: str = Query("en", description="Search language"),
    country: str = Query("us", description="Search country"),
    safe_search: bool = Query(True, description="Enable safe search"),
    settings: Settings = Depends(get_settings)
):
    # Convert GET request to SearchRequest and call the POST endpoint handler
    request = SearchRequest(
        query=query,
        engine=engine,
        num_results=num_results,
        language=language,
        country=country,
        safe_search=safe_search
    )
    return await search(request, settings)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)