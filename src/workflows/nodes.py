"""
Workflow nodes for the NewsGenie LangGraph
Each node represents a step in the query processing pipeline
"""
from typing import Dict, Any
from src.workflows.state import GraphState
from src.agents.chatbot import NewsGenieAgent
from src.tools.news_fetcher import NewsFetcher
from src.tools.web_search import WebSearchTool
from src.config import settings


# Initialize tools (singleton pattern)
chatbot_agent = None
news_fetcher = None
web_search_tool = None


def get_chatbot_agent() -> NewsGenieAgent:
    """Get or create chatbot agent instance"""
    global chatbot_agent
    if chatbot_agent is None:
        chatbot_agent = NewsGenieAgent()
    return chatbot_agent


def get_news_fetcher() -> NewsFetcher:
    """Get or create news fetcher instance"""
    global news_fetcher
    if news_fetcher is None:
        news_fetcher = NewsFetcher()
    return news_fetcher


def get_web_search_tool() -> WebSearchTool:
    """Get or create web search tool instance"""
    global web_search_tool
    if web_search_tool is None:
        web_search_tool = WebSearchTool()
    return web_search_tool


def classify_query_node(state: GraphState) -> GraphState:
    """
    Node: Classify the user's query as news-related or general
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with classification results
    """
    print("🔍 Classifying query...")
    
    try:
        agent = get_chatbot_agent()
        user_input = state["user_input"]
        
        # Classify the query
        classification = agent.classify_query(user_input)
        
        state["query_classification"] = classification
        state["metadata"]["classification_confidence"] = classification.get("confidence", 0.0)
        
        print(f"   Classification: {'News' if classification['is_news_request'] else 'General'}")
        print(f"   Confidence: {classification['confidence']:.2f}")
        
    except Exception as e:
        state["error"] = f"Classification error: {str(e)}"
        print(f"❌ Error: {e}")
    
    return state


def fetch_news_node(state: GraphState) -> GraphState:
    """
    Node: Fetch news articles based on the query
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with news results
    """
    print("📰 Fetching news...")
    
    try:
        fetcher = get_news_fetcher()
        user_input = state["user_input"]
        
        # Try to extract category or use search
        query_lower = user_input.lower()
        category = None
        
        # Check if query mentions a specific category
        for cat in settings.news_categories:
            if cat in query_lower:
                category = cat
                break
        
        # Fetch news
        if category:
            print(f"   Using category: {category}")
            results = fetcher.get_news_by_category(category)
        else:
            print(f"   Searching for: {user_input}")
            results = fetcher.search_news(user_input, page_size=5)
        
        state["news_results"] = results
        
        if results["status"] == "success":
            print(f"   ✅ Found {len(results['articles'])} articles")
        else:
            print(f"   ⚠️ {results['message']}")
        
    except Exception as e:
        state["error"] = f"News fetch error: {str(e)}"
        print(f"❌ Error: {e}")
    
    return state


def web_search_node(state: GraphState) -> GraphState:
    """
    Node: Perform web search for additional context
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with web search results
    """
    print("🔎 Performing web search...")
    
    try:
        search_tool = get_web_search_tool()
        user_input = state["user_input"]
        
        # Perform search
        results = search_tool.search(user_input, max_results=5)
        
        state["web_search_results"] = results
        
        if results["status"] == "success":
            print(f"   ✅ Found {len(results['results'])} results")
        else:
            print(f"   ⚠️ {results['message']}")
        
    except Exception as e:
        # Don't fail the entire workflow if web search fails
        state["web_search_results"] = {
            "status": "error",
            "message": str(e),
            "results": []
        }
        print(f"⚠️ Web search failed: {e}")
    
    return state


def generate_response_node(state: GraphState) -> GraphState:
    """
    Node: Generate final response using the chatbot and collected information
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with final response
    """
    print("💬 Generating response...")
    
    try:
        agent = get_chatbot_agent()
        user_input = state["user_input"]
        chat_history = state.get("chat_history", [])
        
        # Build context from news and search results
        context_parts = []
        
        # Add news results if available
        news_results = state.get("news_results")
        if news_results and news_results.get("status") == "success":
            articles = news_results.get("articles", [])
            if articles:
                context_parts.append("**Recent News Articles:**\n")
                for i, article in enumerate(articles[:5], 1):
                    context_parts.append(
                        f"{i}. {article['title']}\n"
                        f"   Source: {article['source']}\n"
                        f"   {article['description']}\n"
                        f"   URL: {article['url']}\n"
                    )
        
        # Add web search results if available
        web_results = state.get("web_search_results")
        if web_results and web_results.get("status") == "success":
            results = web_results.get("results", [])
            if results and not news_results:  # Only add if no news results
                context_parts.append("\n**Additional Information:**\n")
                for i, result in enumerate(results[:3], 1):
                    context_parts.append(
                        f"{i}. {result['title']}\n"
                        f"   {result['snippet']}\n"
                        f"   URL: {result['url']}\n"
                    )
        
        # Combine context
        context = "\n".join(context_parts) if context_parts else ""
        
        # Create enhanced prompt
        if context:
            enhanced_input = f"""Based on the following information, please answer the user's question:

{context}

User's question: {user_input}

Please provide a helpful, informative response that synthesizes the information above."""
        else:
            enhanced_input = user_input
        
        # Generate response
        formatted_history = agent.format_chat_history(chat_history)
        response = agent.chat(enhanced_input, formatted_history)
        
        state["final_response"] = response
        print("   ✅ Response generated")
        
    except Exception as e:
        state["error"] = f"Response generation error: {str(e)}"
        state["final_response"] = f"I apologize, but I encountered an error: {str(e)}"
        print(f"❌ Error: {e}")
    
    return state


def handle_general_query_node(state: GraphState) -> GraphState:
    """
    Node: Handle general (non-news) queries directly with the chatbot
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with response
    """
    print("💭 Handling general query...")
    
    try:
        agent = get_chatbot_agent()
        user_input = state["user_input"]
        chat_history = state.get("chat_history", [])
        
        # Generate response directly
        formatted_history = agent.format_chat_history(chat_history)
        response = agent.chat(user_input, formatted_history)
        
        state["final_response"] = response
        print("   ✅ Response generated")
        
    except Exception as e:
        state["error"] = f"General query error: {str(e)}"
        state["final_response"] = f"I apologize, but I encountered an error: {str(e)}"
        print(f"❌ Error: {e}")
    
    return state