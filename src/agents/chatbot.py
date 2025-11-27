"""
Main chatbot agent for NewsGenie
Handles general queries and conversation management
"""
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough

from src.config import settings


class NewsGenieAgent:
    """
    Main chatbot agent that handles conversations and routes requests
    """
    
    def __init__(self):
        """Initialize the chatbot agent"""
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            api_key=settings.openai_api_key
        )
        
        # System prompt for the agent
        self.system_prompt = """You are NewsGenie, an intelligent AI assistant specialized in news aggregation and general conversation.

Your capabilities:
1. Answer general questions on any topic with helpful, accurate information
2. Help users find and understand news articles
3. Provide context and analysis for current events
4. Maintain engaging, friendly conversations

When users ask about news or current events, you should:
- Help them find relevant, recent news articles
- Summarize key points clearly
- Provide context and background information
- Cite sources when discussing specific news

When users ask general questions, you should:
- Provide helpful, accurate responses
- Be conversational and friendly
- Ask clarifying questions when needed

Always be informative, objective, and helpful."""

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify if a query is news-related or general
        
        Args:
            query: User's input query
            
        Returns:
            Dictionary with classification results
        """
        classification_prompt = f"""Analyze this user query and determine if it's requesting news/current events or if it's a general question.

User query: "{query}"

Respond with ONLY a JSON object in this exact format:
{{
    "is_news_request": true or false,
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation"
}}

A query is news-related if it:
- Asks about current events, recent news, or breaking news
- Requests news in specific categories (business, tech, sports, etc.)
- Asks "what's happening" or "latest news"
- References recent/current events

A query is general if it:
- Asks for explanations, definitions, or how-to information
- Requests recommendations or advice
- Is conversational or personal
- Asks about historical facts or timeless information"""

        try:
            response = self.llm.invoke([HumanMessage(content=classification_prompt)])
            
            # Parse the response
            import json
            # Remove markdown code blocks if present
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"Error classifying query: {e}")
            # Default to general query on error
            return {
                "is_news_request": False,
                "confidence": 0.5,
                "reasoning": "Classification error, defaulting to general query"
            }
    
    def chat(self, user_input: str, chat_history: List = None) -> str:
        """
        Process a user message and generate a response
        
        Args:
            user_input: The user's message
            chat_history: Previous conversation history
            
        Returns:
            AI response as string
        """
        if chat_history is None:
            chat_history = []
        
        try:
            # Invoke the chain
            response = self.chain.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            
            return response.content
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def format_chat_history(self, messages: List[Dict[str, str]]) -> List:
        """
        Format chat history for the LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            List of LangChain message objects
        """
        formatted = []
        for msg in messages:
            if msg["role"] == "user":
                formatted.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted.append(AIMessage(content=msg["content"]))
        return formatted