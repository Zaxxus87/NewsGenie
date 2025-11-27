"""
Web search tool using DuckDuckGo for additional information retrieval
"""
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS


class WebSearchTool:
    """
    Tool for searching the web using DuckDuckGo
    """
    
    def __init__(self, max_results: int = 5):
        """
        Initialize the web search tool
        
        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results
        self.ddgs = DDGS()
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        region: str = "wt-wt"
    ) -> Dict[str, Any]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query string
            max_results: Maximum number of results (overrides default)
            region: Region code for search (default: wt-wt for worldwide)
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            max_results = max_results or self.max_results
            
            # Perform the search
            results = list(self.ddgs.text(
                keywords=query,
                region=region,
                max_results=max_results
            ))
            
            return self._format_response(results, query)
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}",
                "results": []
            }
    
    def search_news(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for news articles using DuckDuckGo News
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            
        Returns:
            Dictionary containing news results and metadata
        """
        try:
            max_results = max_results or self.max_results
            
            # Perform news search
            results = list(self.ddgs.news(
                keywords=query,
                max_results=max_results
            ))
            
            return self._format_news_response(results, query)
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"News search failed: {str(e)}",
                "results": []
            }
    
    def _format_response(
        self,
        results: List[Dict],
        query: str
    ) -> Dict[str, Any]:
        """
        Format web search results
        
        Args:
            results: Raw search results from DuckDuckGo
            query: Original search query
            
        Returns:
            Formatted response dictionary
        """
        if not results:
            return {
                "status": "success",
                "query": query,
                "total_results": 0,
                "results": [],
                "message": "No results found"
            }
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", "No title"),
                "snippet": result.get("body", "No description available"),
                "url": result.get("href", ""),
                "source": result.get("href", "").split("/")[2] if result.get("href") else "Unknown"
            })
        
        return {
            "status": "success",
            "query": query,
            "total_results": len(formatted_results),
            "results": formatted_results,
            "message": f"Found {len(formatted_results)} results"
        }
    
    def _format_news_response(
        self,
        results: List[Dict],
        query: str
    ) -> Dict[str, Any]:
        """
        Format news search results
        
        Args:
            results: Raw news results from DuckDuckGo
            query: Original search query
            
        Returns:
            Formatted response dictionary
        """
        if not results:
            return {
                "status": "success",
                "query": query,
                "total_results": 0,
                "results": [],
                "message": "No news found"
            }
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", "No title"),
                "snippet": result.get("body", "No description available"),
                "url": result.get("url", ""),
                "source": result.get("source", "Unknown"),
                "date": result.get("date", "Unknown date"),
                "image": result.get("image", "")
            })
        
        return {
            "status": "success",
            "query": query,
            "total_results": len(formatted_results),
            "results": formatted_results,
            "message": f"Found {len(formatted_results)} news articles"
        }
    
    def format_results_for_display(
        self,
        results: List[Dict],
        result_type: str = "web"
    ) -> str:
        """
        Format search results into a readable string
        
        Args:
            results: List of result dictionaries
            result_type: Type of results ("web" or "news")
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            if result_type == "news":
                formatted.append(f"""
**{i}. {result['title']}**
Source: {result['source']} | Date: {result['date']}
{result['snippet']}
Read more: {result['url']}
""")
            else:
                formatted.append(f"""
**{i}. {result['title']}**
Source: {result['source']}
{result['snippet']}
Link: {result['url']}
""")
        
        return "\n".join(formatted)