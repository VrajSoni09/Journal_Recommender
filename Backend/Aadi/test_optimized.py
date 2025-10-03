"""
Test script for optimized fetch_journals.py
Tests functionality without making actual API calls (uses mock data)
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_validation():
    """Test input validation logic"""
    print("\n" + "="*80)
    print("TEST 1: Input Validation")
    print("="*80)
    
    from fetch_journals_optimized import OpenAlexJournalFetcher
    fetcher = OpenAlexJournalFetcher()
    
    # Test valid criteria
    valid_criteria = {
        "subjectArea": "Machine Learning",
        "keywords": ["deep learning", "neural networks", "AI", "computer vision", "NLP"],
        "openAccess": 1,
        "acceptancePercentFrom": 20,
        "acceptancePercentTo": 40
    }
    
    is_valid, errors = fetcher.validate_criteria(valid_criteria)
    assert is_valid, f"Valid criteria marked as invalid: {errors}"
    print("✓ Valid criteria test passed")
    
    # Test missing required field
    invalid_criteria = {
        "subjectArea": "Machine Learning",
        "openAccess": 1
    }
    
    is_valid, errors = fetcher.validate_criteria(invalid_criteria)
    assert not is_valid, "Invalid criteria marked as valid"
    assert len(errors) > 0, "No errors reported for invalid criteria"
    print(f"✓ Missing field test passed (errors: {errors})")
    
    # Test invalid openAccess value
    invalid_oa = {
        "subjectArea": "Machine Learning",
        "keywords": ["AI", "ML", "deep learning", "neural networks", "NLP"],
        "openAccess": 2  # Invalid
    }
    
    is_valid, errors = fetcher.validate_criteria(invalid_oa)
    assert not is_valid, "Invalid openAccess marked as valid"
    print(f"✓ Invalid openAccess test passed (errors: {errors})")
    
    print("\n[PASS] All validation tests passed ✓")


def test_search_query_building():
    """Test search query construction"""
    print("\n" + "="*80)
    print("TEST 2: Search Query Building")
    print("="*80)
    
    from fetch_journals_optimized import OpenAlexJournalFetcher
    fetcher = OpenAlexJournalFetcher()
    
    criteria = {
        "subjectArea": "Artificial Intelligence",
        "keywords": ["machine learning", "deep learning", "neural networks", 
                    "computer vision", "NLP", "transformers", "GPT", "BERT",
                    "reinforcement learning", "supervised learning", "unsupervised learning"]
    }
    
    query = fetcher.build_search_query(criteria)
    
    # Check subject area is included
    assert "Artificial Intelligence" in query, "Subject area not in query"
    print(f"✓ Subject area included")
    
    # Check keywords are included (should be limited to 10)
    assert "machine learning" in query or "deep learning" in query, "Keywords not in query"
    print(f"✓ Keywords included")
    
    # Check query uses OR operator
    assert " OR " in query, "OR operator not used"
    print(f"✓ OR operator used for keywords")
    
    print(f"\nGenerated query (truncated): {query[:150]}...")
    print("\n[PASS] Search query building tests passed ✓")


def test_journal_scoring():
    """Test journal scoring algorithm"""
    print("\n" + "="*80)
    print("TEST 3: Journal Scoring Algorithm")
    print("="*80)
    
    from fetch_journals_optimized import OpenAlexJournalFetcher
    fetcher = OpenAlexJournalFetcher()
    
    # Mock journal data
    excellent_journal = {
        "display_name": "Nature Machine Intelligence",
        "summary_stats": {"h_index": 180},
        "cited_by_count": 95000,
        "is_oa": True,
        "is_in_doaj": True
    }
    
    good_journal = {
        "display_name": "Journal of AI Research",
        "summary_stats": {"h_index": 100},
        "cited_by_count": 50000,
        "is_oa": False,
        "is_in_doaj": False
    }
    
    poor_journal = {
        "display_name": "New AI Journal",
        "summary_stats": {"h_index": 10},
        "cited_by_count": 1000,
        "is_oa": False,
        "is_in_doaj": False
    }
    
    # Test scoring
    excellent_score = fetcher.calculate_journal_score(excellent_journal, relevance_count=12)
    good_score = fetcher.calculate_journal_score(good_journal, relevance_count=5)
    poor_score = fetcher.calculate_journal_score(poor_journal, relevance_count=1)
    
    print(f"Excellent journal score: {excellent_score}/100")
    print(f"Good journal score: {good_score}/100")
    print(f"Poor journal score: {poor_score}/100")
    
    # Verify scoring logic
    assert excellent_score > good_score, "Excellent journal scored lower than good journal"
    assert good_score > poor_score, "Good journal scored lower than poor journal"
    assert 0 <= excellent_score <= 100, "Score out of bounds"
    print("\n✓ Scoring hierarchy correct")
    
    # Test max score components
    assert excellent_score > 80, "Excellent journal should score > 80"
    print("✓ Excellent journal scored appropriately high")
    
    print("\n[PASS] Journal scoring tests passed ✓")


def test_output_formatting():
    """Test output formatting"""
    print("\n" + "="*80)
    print("TEST 4: Output Formatting")
    print("="*80)
    
    from fetch_journals_optimized import OpenAlexJournalFetcher
    fetcher = OpenAlexJournalFetcher()
    
    # Mock journal data
    mock_journal = {
        "id": "https://openalex.org/S12345678",
        "display_name": "Nature Machine Intelligence",
        "issn": ["2522-5839"],
        "issn_l": "2522-5839",
        "host_organization_name": "Springer Nature",
        "homepage_url": "https://www.nature.com/natmachintell/",
        "summary_stats": {"h_index": 45, "i10_index": 120},
        "cited_by_count": 15678,
        "works_count": 456,
        "is_oa": False,
        "is_in_doaj": False,
        "apc_usd": 9500,
        "societies": [],
        "type": "journal",
        "relevance_count": 8,
        "calculated_score": 72.45
    }
    
    formatted = fetcher.format_journal_output(mock_journal, rank=1)
    
    # Check required fields
    required_fields = [
        "rank", "journal_name", "issn", "publisher", "homepage_url",
        "h_index", "cited_by_count", "is_open_access", "calculated_score"
    ]
    
    for field in required_fields:
        assert field in formatted, f"Missing required field: {field}"
    
    print("✓ All required fields present")
    
    # Check values
    assert formatted["rank"] == 1, "Rank not set correctly"
    assert formatted["journal_name"] == "Nature Machine Intelligence", "Name not formatted"
    assert formatted["calculated_score"] == 72.45, "Score not preserved"
    print("✓ Values formatted correctly")
    
    # Print sample output
    print("\nSample formatted output:")
    print(json.dumps(formatted, indent=2))
    
    print("\n[PASS] Output formatting tests passed ✓")


def test_file_loading():
    """Test input file loading with fallbacks"""
    print("\n" + "="*80)
    print("TEST 5: File Loading & Fallbacks")
    print("="*80)
    
    from fetch_journals_optimized import OpenAlexJournalFetcher
    fetcher = OpenAlexJournalFetcher()
    
    # Try to load from format.json (should exist)
    criteria = fetcher.load_search_criteria('format.json')
    
    if criteria:
        print(f"✓ Successfully loaded format.json")
        print(f"  Subject: {criteria.get('subjectArea', 'N/A')}")
        print(f"  Keywords: {len(criteria.get('keywords', []))} items")
    else:
        print("⚠ format.json not found (this is OK for testing)")
    
    # Try non-existent file
    no_file = fetcher.load_search_criteria('nonexistent.json')
    assert no_file is None, "Should return None for missing file"
    print("✓ Returns None for missing file")
    
    print("\n[PASS] File loading tests passed ✓")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "█"*80)
    print("RUNNING OPTIMIZED CODE TESTS")
    print("█"*80)
    
    try:
        test_validation()
        test_search_query_building()
        test_journal_scoring()
        test_output_formatting()
        test_file_loading()
        
        print("\n" + "█"*80)
        print("ALL TESTS PASSED ✓✓✓")
        print("█"*80)
        print("\nOptimized code is ready for production!")
        return True
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
