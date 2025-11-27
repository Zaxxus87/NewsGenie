"""
LangGraph workflow definition for NewsGenie
Orchestrates the query processing pipeline
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from src.workflows.state import GraphState
from src.workflows.nodes import (
    classify_query_node,
    fetch_news_node,
    web_search_node,
    generate_response_node,
    handle_general_query_node
)


def should_fetch_news(state: GraphState) -> Literal["fetch_news", "handle_general"]:
    """
    Router: Determine if we should fetch news or handle as general query
    
    Args:
        state: Current graph state
        
    Returns:
        Next node name to route to
    """
    classification = state.get("query_classification", {})
    is_news = classification.get("is_news_request", False)
    confidence = classification.get("confidence", 0.0)
    
    # Route to news fetching if classified as news with reasonable confidence
    if is_news and confidence > 0.6:
        return "fetch_news"
    else:
        return "handle_general"


def should_add_web_search(state: GraphState) -> Literal["web_search", "generate_response"]:
    """
    Router: Determine if we should add web search or proceed to response generation
    
    Args:
        state: Current graph state
        
    Returns:
        Next node name to route to
    """
    news_results = state.get("news_results", {})
    
    # Add web search if news fetch failed or returned limited results
    if news_results.get("status") == "error":
        return "web_search"
    
    articles = news_results.get("articles", [])
    if len(articles) < 3:
        return "web_search"
    
    # Otherwise, proceed directly to response generation
    return "generate_response"


def create_workflow() -> StateGraph:
    """
    Create and configure the NewsGenie workflow graph
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes to the graph
    workflow.add_node("classify_query", classify_query_node)
    workflow.add_node("fetch_news", fetch_news_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate_response", generate_response_node)
    workflow.add_node("handle_general", handle_general_query_node)
    
    # Set entry point
    workflow.set_entry_point("classify_query")
    
    # Add conditional routing from classification
    workflow.add_conditional_edges(
        "classify_query",
        should_fetch_news,
        {
            "fetch_news": "fetch_news",
            "handle_general": "handle_general"
        }
    )
    
    # Add conditional routing from news fetching
    workflow.add_conditional_edges(
        "fetch_news",
        should_add_web_search,
        {
            "web_search": "web_search",
            "generate_response": "generate_response"
        }
    )
    
    # Add edge from web search to response generation
    workflow.add_edge("web_search", "generate_response")
    
    # Add edges to END
    workflow.add_edge("generate_response", END)
    workflow.add_edge("handle_general", END)
    
    # Compile the graph
    return workflow.compile()


def run_workflow(user_input: str, chat_history: list = None) -> dict:
    """
    Execute the workflow for a given user input
    
    Args:
        user_input: The user's query
        chat_history: Previous conversation messages
        
    Returns:
        Dictionary containing the final state with response
    """
    if chat_history is None:
        chat_history = []
    
    # Initialize state
    initial_state = {
        "user_input": user_input,
        "chat_history": chat_history,
        "query_classification": None,
        "news_results": None,
        "web_search_results": None,
        "final_response": "",
        "error": None,
        "metadata": {}
    }
    
    # Create and run workflow
    print(f"\n{'='*60}")
    print(f"Processing query: {user_input}")
    print(f"{'='*60}")
    
    workflow = create_workflow()
    final_state = workflow.invoke(initial_state)
    
    print(f"{'='*60}")
    print("Workflow completed!")
    print(f"{'='*60}\n")
    
    return final_state