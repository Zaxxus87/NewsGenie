"""
State definitions for the NewsGenie LangGraph workflow
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator


class GraphState(TypedDict):
    """
    State schema for the NewsGenie workflow graph
    
    Attributes:
        user_input: The user's query or message
        chat_history: List of previous messages in the conversation
        query_classification: Classification results (news vs general query)
        news_results: Results from news API
        web_search_results: Results from web search
        final_response: The generated response to return to user
        error: Any error messages encountered
        metadata: Additional metadata about the query processing
    """
    # Core inputs
    user_input: str
    chat_history: Annotated[List[Dict[str, str]], operator.add]
    
    # Classification
    query_classification: Optional[Dict[str, Any]]
    
    # Tool results
    news_results: Optional[Dict[str, Any]]
    web_search_results: Optional[Dict[str, Any]]
    
    # Output
    final_response: str
    
    # Error handling
    error: Optional[str]
    
    # Metadata
    metadata: Dict[str, Any]