
import sys
from unittest.mock import MagicMock

# Mock httpx before importing the service
sys.modules['httpx'] = MagicMock()

from backend.services.perplexity_intelligence import PerplexityIntelligenceService

def test_extract_domain():
    service = PerplexityIntelligenceService(api_key="pplx-test")

    # Test cases
    test_cases = [
        ("https://www.bloomberg.com/news/articles", "bloomberg.com"),
        ("https://reuters.com/business", "reuters.com"),
        ("http://cnbc.com", "cnbc.com"),
        ("invalid-url", ""), # urlparse("invalid-url").netloc is ""
        (None, None), # urlparse(None) raises Exception, returns url which is None
    ]

    for url, expected in test_cases:
        result = service._extract_domain(url)
        print(f"URL: {url} -> Result: {result} (Expected: {expected})")
        assert result == expected

if __name__ == "__main__":
    try:
        test_extract_domain()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed!")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
