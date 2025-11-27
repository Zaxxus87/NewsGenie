"""
Test news fetcher and web search tools
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.tools.news_fetcher import NewsFetcher
from src.tools.web_search import WebSearchTool
from src.config import settings


def test_news_fetcher():
    """Test the News API integration"""
    print("=" * 60)
    print("Testing News Fetcher...")
    print("=" * 60)
    
    # Check if API key is configured
    if not settings.news_api_key:
        print("⚠️  NEWS_API_KEY not configured in .env file")
        print("   Skipping News Fetcher tests")
        return False
    
    try:
        fetcher = NewsFetcher()
        print("✅ News Fetcher initialized successfully!")
        
        # Test 1: Get top headlines
        print("\n[Test 1] Fetching top headlines...")
        response = fetcher.get_top_headlines(page_size=3)
        
        if response["status"] == "success":
            print(f"✅ Found {response['total_results']} total articles")
            print(f"   Retrieved {len(response['articles'])} articles")
            
            if response['articles']:
                print("\n   Sample article:")
                article = response['articles'][0]
                print(f"   Title: {article['title']}")
                print(f"   Source: {article['source']}")
        else:
            print(f"❌ Error: {response['message']}")
            return False
        
        # Test 2: Get news by category
        print("\n[Test 2] Fetching technology news...")
        response = fetcher.get_news_by_category("technology")
        
        if response["status"] == "success":
            print(f"✅ Found {len(response['articles'])} technology articles")
        else:
            print(f"❌ Error: {response['message']}")
            return False
        
        # Test 3: Search news
        print("\n[Test 3] Searching for 'artificial intelligence'...")
        response = fetcher.search_news("artificial intelligence", page_size=3)
        
        if response["status"] == "success":
            print(f"✅ Found {response['total_results']} total results")
            print(f"   Retrieved {len(response['articles'])} articles")
        else:
            print(f"❌ Error: {response['message']}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All News Fetcher tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error testing News Fetcher: {e}")
        return False


def test_web_search():
    """Test the DuckDuckGo web search tool"""
    print("\n" + "=" * 60)
    print("Testing Web Search Tool...")
    print("=" * 60)
    
    try:
        search_tool = WebSearchTool(max_results=3)
        print("✅ Web Search Tool initialized successfully!")
        
        # Test 1: Basic web search
        print("\n[Test 1] Searching for 'Python programming'...")
        response = search_tool.search("Python programming", max_results=3)
        
        if response["status"] == "success":
            print(f"✅ Found {response['total_results']} results")
            
            if response['results']:
                print("\n   Sample result:")
                result = response['results'][0]
                print(f"   Title: {result['title']}")
                print(f"   Source: {result['source']}")
        else:
            print(f"❌ Error: {response['message']}")
            return False
        
        # Test 2: News search
        print("\n[Test 2] Searching news for 'technology'...")
        response = search_tool.search_news("technology", max_results=3)
        
        if response["status"] == "success":
            print(f"✅ Found {response['total_results']} news articles")
        else:
            print(f"❌ Error: {response['message']}")
            return False
        
        # Test 3: Format results for display
        print("\n[Test 3] Testing result formatting...")
        if response['results']:
            formatted = search_tool.format_results_for_display(
                response['results'][:2],
                result_type="news"
            )
            print("✅ Results formatted successfully")
            print("\n   Formatted output preview:")
            print(formatted[:200] + "...")
        
        print("\n" + "=" * 60)
        print("✅ All Web Search tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error testing Web Search: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔧 NewsGenie Tools Testing Suite\n")
    
    news_passed = test_news_fetcher()
    web_passed = test_web_search()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"News Fetcher: {'✅ PASSED' if news_passed else '❌ FAILED'}")
    print(f"Web Search:   {'✅ PASSED' if web_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if news_passed and web_passed:
        print("\n🎉 All tools are working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")