"""
News API integration tool for fetching real-time news articles
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from newsapi import NewsApiClient

from src.config import settings


class NewsFetcher:
    """
    Tool for fetching news articles from NewsAPI
    """
    
    def __init__(self):
        """Initialize the News API client"""
        if not settings.news_api_key:
            raise ValueError("NEWS_API_KEY not found in environment variables")
        
        self.client = NewsApiClient(api_key=settings.news_api_key)
        self.page_size = settings.news_api_page_size
    
    def get_top_headlines(
        self,
        category: Optional[str] = None,
        country: str = "us",
        page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch top headlines from NewsAPI
        
        Args:
            category: News category (business, technology, etc.)
            country: Country code (default: us)
            page_size: Number of articles to fetch
            
        Returns:
            Dictionary containing articles and metadata
        """
        try:
            page_size = page_size or self.page_size
            
            response = self.client.get_top_headlines(
                category=category,
                country=country,
                page_size=page_size
            )
            
            return self._format_response(response)
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to fetch top headlines: {str(e)}",
                "articles": []
            }
    
    def search_news(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for news articles by query
        
        Args:
            query: Search query string
            from_date: Start date for articles
            to_date: End date for articles
            language: Language code (default: en)
            sort_by: Sort order (publishedAt, relevancy, popularity)
            page_size: Number of articles to fetch
            
        Returns:
            Dictionary containing articles and metadata
        """
        try:
            page_size = page_size or self.page_size
            
            # Default to last 7 days if no dates provided
            if not from_date:
                from_date = datetime.now() - timedelta(days=7)
            if not to_date:
                to_date = datetime.now()
            
            response = self.client.get_everything(
                q=query,
                from_param=from_date.strftime("%Y-%m-%d"),
                to=to_date.strftime("%Y-%m-%d"),
                language=language,
                sort_by=sort_by,
                page_size=page_size
            )
            
            return self._format_response(response)
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to search news: {str(e)}",
                "articles": []
            }
    
    def get_news_by_category(
        self,
        category: str,
        country: str = "us"
    ) -> Dict[str, Any]:
        """
        Convenience method to get news by category
        
        Args:
            category: News category
            country: Country code
            
        Returns:
            Dictionary containing articles and metadata
        """
        # Validate category
        valid_categories = settings.news_categories
        if category.lower() not in valid_categories:
            return {
                "status": "error",
                "message": f"Invalid category. Valid options: {', '.join(valid_categories)}",
                "articles": []
            }
        
        return self.get_top_headlines(category=category.lower(), country=country)
    
    def _format_response(self, response: Dict) -> Dict[str, Any]:
        """
        Format the NewsAPI response into a consistent structure
        
        Args:
            response: Raw response from NewsAPI
            
        Returns:
            Formatted response dictionary
        """
        if response.get("status") != "ok":
            return {
                "status": "error",
                "message": "Failed to fetch news",
                "articles": []
            }
        
        articles = response.get("articles", [])
        
        # Format each article
        formatted_articles = []
        for article in articles:
            formatted_articles.append({
                "title": article.get("title", "No title"),
                "description": article.get("description", "No description available"),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "author": article.get("author", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "content": article.get("content", ""),
                "image_url": article.get("urlToImage", "")
            })
        
        return {
            "status": "success",
            "total_results": response.get("totalResults", 0),
            "articles": formatted_articles,
            "message": f"Found {len(formatted_articles)} articles"
        }
    
    def format_articles_for_display(self, articles: List[Dict]) -> str:
        """
        Format articles into a readable string for the chatbot
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Formatted string
        """
        if not articles:
            return "No articles found."
        
        formatted = []
        for i, article in enumerate(articles, 1):
            formatted.append(f"""
**{i}. {article['title']}**
Source: {article['source']}
Published: {article['published_at']}
{article['description']}
Read more: {article['url']}
""")
        
        return "\n".join(formatted)