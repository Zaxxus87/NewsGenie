"""
NewsGenie - AI-Powered News Assistant
Main Streamlit Application
"""
import streamlit as st
from datetime import datetime
from src.workflows.graph import run_workflow
from src.config import settings

# Page configuration
st.set_page_config(
    page_title=settings.app_title,
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1f77b4;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "workflow_running" not in st.session_state:
        st.session_state.workflow_running = False


def validate_api_keys():
    """Check if API keys are configured"""
    validation = settings.validate_api_keys()
    if not validation["valid"]:
        st.error("⚠️ Missing API Keys")
        st.write("Please configure the following API keys in your `.env` file:")
        for key in validation["missing_keys"]:
            st.code(f"{key}=your_key_here")
        st.info("After adding API keys, restart the application.")
        return False
    return True


def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_user_input(user_input: str):
    """Process user input through the workflow"""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Show assistant is thinking
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Run the workflow
                result = run_workflow(
                    user_input=user_input,
                    chat_history=st.session_state.chat_history
                )
                
                # Get the response
                response = result.get("final_response", "I apologize, but I couldn't generate a response.")
                
                # Check for errors
                if result.get("error"):
                    response = f"⚠️ {result['error']}\n\n{response}"
                
                # Display response
                st.markdown(response)
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Update conversation history for context
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
                
            except Exception as e:
                error_msg = f"❌ An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })


def main():
    """Main application"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">📰 NewsGenie</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">{settings.app_description}</div>',
        unsafe_allow_html=True
    )
    
    # Validate API keys
    if not validate_api_keys():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # News Categories
        st.subheader("📑 News Categories")
        st.write("Available categories:")
        for category in settings.news_categories:
            st.write(f"• {category.title()}")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        
        # Sample Queries
        st.subheader("💡 Sample Queries")
        sample_queries = [
            "What's the latest technology news?",
            "Show me business headlines",
            "Tell me about recent AI developments",
            "What's happening in sports?",
            "How do I learn Python?"
        ]
        
        for query in sample_queries:
            if st.button(query, key=f"sample_{query}"):
                st.session_state.sample_query = query
        
        st.markdown("---")
        
        # Statistics
        st.subheader("📊 Session Stats")
        st.metric("Messages", len(st.session_state.messages))
        st.metric("Conversations", len(st.session_state.chat_history) // 2)
        
        st.markdown("---")
        
        # About
        st.subheader("ℹ️ About")
        st.write(f"**Model:** {settings.openai_model}")
        st.write("**Version:** 1.0.0")
        st.write("Built with ❤️ using LangChain & Streamlit")
    
    # Main chat area
    st.markdown("---")
    
    # Display chat history
    display_chat_history()
    
    # Handle sample query button click
    if hasattr(st.session_state, 'sample_query'):
        query = st.session_state.sample_query
        del st.session_state.sample_query
        process_user_input(query)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about news or general topics..."):
        process_user_input(prompt)
        st.rerun()
    
    # Welcome message for first visit
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant"):
            st.markdown("""
👋 **Welcome to NewsGenie!**

I'm your AI-powered news assistant. I can help you with:

- 📰 **Latest News**: Get top headlines from various categories
- 🔍 **News Search**: Find specific news articles on any topic
- 💬 **General Questions**: Answer questions on any subject
- 🎯 **Smart Routing**: Automatically fetch the most relevant information

**Try asking:**
- "What's the latest technology news?"
- "Tell me about recent AI developments"
- "Show me business headlines"
- Or any general question you have!

How can I help you today?
            """)


if __name__ == "__main__":
    main()