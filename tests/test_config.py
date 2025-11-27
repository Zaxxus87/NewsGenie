"""
Test configuration and agent initialization
"""
from src.config import settings
from src.agents.chatbot import NewsGenieAgent


def test_config():
    """Test configuration loading"""
    print("=" * 60)
    print("Testing Configuration...")
    print("=" * 60)
    print(f"App Title: {settings.app_title}")
    print(f"App Description: {settings.app_description}")
    print(f"Model: {settings.openai_model}")
    print(f"Temperature: {settings.temperature}")
    print(f"Max Tokens: {settings.max_tokens}")
    
    # Validate API keys
    validation = settings.validate_api_keys()
    print(f"\n{'='*60}")
    print("API Key Validation")
    print("=" * 60)
    print(f"Valid: {validation['valid']}")
    
    if not validation["valid"]:
        print(f"⚠️  Missing API Keys: {', '.join(validation['missing_keys'])}")
        print("\n📝 Please add these keys to your .env file:")
        for key in validation['missing_keys']:
            print(f"   {key}=your_key_here")
        return False
    else:
        print("✅ All API keys configured!")
        return True


def test_agent():
    """Test agent initialization"""
    print(f"\n{'='*60}")
    print("Testing Agent Initialization...")
    print("=" * 60)
    
    try:
        agent = NewsGenieAgent()
        print("✅ NewsGenieAgent initialized successfully!")
        
        # Test query classification
        print(f"\n{'='*60}")
        print("Testing Query Classification...")
        print("=" * 60)
        
        test_queries = [
            "What's the latest news in technology?",
            "How do I bake a chocolate cake?",
            "Tell me about recent developments in AI",
            "What is Python programming?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n[Test {i}/4]")
            print(f"Query: '{query}'")
            result = agent.classify_query(query)
            print(f"  → News Request: {result['is_news_request']}")
            print(f"  → Confidence: {result['confidence']:.2f}")
            print(f"  → Reasoning: {result['reasoning']}")
        
        print(f"\n{'='*60}")
        print("✅ All tests passed!")
        print("=" * 60)
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    config_valid = test_config()
    
    if config_valid:
        test_agent()
    else:
        print("\n⚠️  Please configure API keys before testing the agent.")