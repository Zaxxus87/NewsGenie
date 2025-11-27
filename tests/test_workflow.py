"""
Test the complete LangGraph workflow
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.workflows.graph import run_workflow
from src.config import settings


def test_workflow():
    """Test the complete workflow with different query types"""
    
    # Check API keys
    validation = settings.validate_api_keys()
    if not validation["valid"]:
        print("⚠️  Missing API Keys:")
        for key in validation["missing_keys"]:
            print(f"   - {key}")
        print("\nPlease configure API keys in .env file before testing")
        return
    
    print("\n" + "="*70)
    print("🧪 NewsGenie Workflow Testing Suite")
    print("="*70)
    
    # Test cases
    test_queries = [
        {
            "query": "What are the latest technology news?",
            "type": "News Query",
            "expected": "news"
        },
        {
            "query": "How do I learn Python programming?",
            "type": "General Query",
            "expected": "general"
        },
        {
            "query": "Tell me about recent AI developments",
            "type": "News Query",
            "expected": "news"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}/{len(test_queries)}: {test_case['type']}")
        print(f"{'='*70}")
        print(f"Query: \"{test_case['query']}\"")
        print()
        
        try:
            # Run workflow
            result = run_workflow(test_case["query"])
            
            # Check for errors
            if result.get("error"):
                print(f"\n❌ Error occurred: {result['error']}")
                results.append(False)
                continue
            
            # Display classification
            classification = result.get("query_classification", {})
            print(f"\n📊 Classification Results:")
            print(f"   Type: {'News Request' if classification.get('is_news_request') else 'General Query'}")
            print(f"   Confidence: {classification.get('confidence', 0):.2f}")
            print(f"   Reasoning: {classification.get('reasoning', 'N/A')}")
            
            # Display results summary
            if result.get("news_results"):
                news = result["news_results"]
                if news.get("status") == "success":
                    print(f"\n📰 News Results: {len(news.get('articles', []))} articles found")
            
            if result.get("web_search_results"):
                web = result["web_search_results"]
                if web.get("status") == "success":
                    print(f"🔎 Web Search: {len(web.get('results', []))} results found")
            
            # Display response preview
            response = result.get("final_response", "")
            print(f"\n💬 Response Preview:")
            print("-" * 70)
            # Show first 300 characters of response
            preview = response[:300] + "..." if len(response) > 300 else response
            print(preview)
            print("-" * 70)
            
            print(f"\n✅ Test Case {i} completed successfully!")
            results.append(True)
            
        except Exception as e:
            print(f"\n❌ Test Case {i} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if all(results):
        print("\n🎉 All workflow tests passed!")
    else:
        print("\n⚠️  Some tests failed. Review the output above for details.")
    
    print(f"{'='*70}\n")


def test_interactive():
    """Interactive mode to test custom queries"""
    print("\n" + "="*70)
    print("🤖 NewsGenie Interactive Workflow Test")
    print("="*70)
    print("Enter your queries to test the workflow (type 'exit' to quit)")
    print()
    
    # Check API keys
    validation = settings.validate_api_keys()
    if not validation["valid"]:
        print("⚠️  Missing API Keys:")
        for key in validation["missing_keys"]:
            print(f"   - {key}")
        print("\nPlease configure API keys in .env file")
        return
    
    chat_history = []
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            if not user_input:
                continue
            
            # Run workflow
            result = run_workflow(user_input, chat_history)
            
            # Display response
            response = result.get("final_response", "No response generated")
            print(f"\nNewsGenie: {response}")
            
            # Update chat history
            chat_history.append({"role": "user", "content": user_input})
            chat_history.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        test_interactive()
    else:
        test_workflow()