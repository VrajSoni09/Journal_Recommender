"""
OpenAlex Journal Fetcher - Optimized Version
============================================
Fetches top research journals from OpenAlex API based on refined search criteria.
Optimized for integration with Vraj's AI refinement system.

Author: Aadi (Optimized)
Date: October 3, 2025
"""

import requests
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Tuple
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class OpenAlexJournalFetcher:
    """
    Fetch and rank research journals from OpenAlex API.
    
    Uses a two-step strategy:
    1. Find top research papers matching criteria
    2. Extract and rank journals where these papers are published
    
    This identifies high-quality journals actively publishing in the research area.
    """
    
    # API Configuration
    WORKS_BASE_URL = "https://api.openalex.org/works"
    SOURCES_BASE_URL = "https://api.openalex.org/sources"
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    # Search Configuration
    TOP_WORKS_COUNT = 30  # Papers to analyze for journal extraction
    TOP_JOURNALS_COUNT = 5  # Final journals to return
    
    # Scoring Weights (must sum to 100)
    WEIGHT_RELEVANCE = 40  # How often journal appears in top works
    WEIGHT_H_INDEX = 30    # Journal impact factor
    WEIGHT_CITATIONS = 20  # Total citations
    WEIGHT_OPEN_ACCESS = 10  # Open access availability
    
    def __init__(self):
        """Initialize the fetcher with API credentials from environment."""
        self.api_key = os.getenv('OPENALEX_API_KEY', '')
        self.email = os.getenv('OPENALEX_EMAIL', '')
        
        if not self.email:
            logger.warning("OPENALEX_EMAIL not set. Using default rate limits.")
        
        logger.info("OpenAlexJournalFetcher initialized")
    
    def load_search_criteria(self, input_file: str = '../Vraj/refined_output.json') -> Optional[Dict[str, Any]]:
        """
        Load search criteria from Vraj's refined output or format.json.
        
        Args:
            input_file: Path to the input JSON file (default: Vraj's output)
        
        Returns:
            Dictionary containing search criteria, or None if error
        """
        # If specific file provided, try only that file
        if input_file != '../Vraj/refined_output.json':
            try:
                path = Path(input_file)
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        criteria = json.load(f)
                    logger.info(f"Loaded search criteria from: {input_file}")
                    return criteria
                else:
                    logger.error(f"Specified file not found: {input_file}")
                    return None
            except Exception as e:
                logger.error(f"Could not load {input_file}: {e}")
                return None
        
        # Default behavior: try multiple possible locations
        # PRIORITY: format.json FIRST (used by api_server), then fallback to old files
        possible_paths = [
            'format.json',
            '../Vraj/refined_output.json',
            './refined_output.json'
        ]
        
        for file_path in possible_paths:
            try:
                path = Path(file_path)
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        criteria = json.load(f)
                    logger.info(f"Loaded search criteria from: {file_path}")
                    return criteria
            except Exception as e:
                logger.debug(f"Could not load {file_path}: {e}")
                continue
        
        logger.error("Could not find input file in any expected location")
        return None
    
    def validate_criteria(self, criteria: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate search criteria has required fields.
        
        Args:
            criteria: Search criteria dictionary
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ['subjectArea', 'keywords', 'openAccess']
        
        for field in required_fields:
            if field not in criteria:
                errors.append(f"Missing required field: {field}")
        
        # Validate keywords
        if 'keywords' in criteria:
            keywords = criteria['keywords']
            if not isinstance(keywords, list) or len(keywords) < 5:
                errors.append("Keywords must be a list with at least 5 items")
        
        # Validate openAccess
        if 'openAccess' in criteria:
            if criteria['openAccess'] not in [0, 1]:
                errors.append("openAccess must be 0 (any) or 1 (free only)")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def build_search_query(self, criteria: Dict[str, Any]) -> str:
        """
        Build optimized search query from criteria.
        
        Args:
            criteria: Search criteria with subjectArea and keywords
        
        Returns:
            Search query string
        """
        query_parts = []
        
        # Add subject area as REQUIRED with AND logic (not just optional)
        if criteria.get('subjectArea'):
            subject = criteria['subjectArea']
            query_parts.append(f"{subject} AND")
        
        # Add top 10 keywords with AND between them for stricter matching
        if criteria.get('keywords'):
            keywords = criteria['keywords'][:10]
            # Use AND between first 5 keywords for stricter, more relevant results
            # This ensures journals MUST match the subject AND core keywords
            keywords_query = ' AND '.join(keywords[:5])
            query_parts.append(f"({keywords_query})")
        
        query = ' '.join(query_parts)
        logger.debug(f"Built search query: {query[:100]}...")
        return query
    
    def make_request_with_retry(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make API request with retry logic and error handling.
        
        Args:
            url: API endpoint URL
            params: Request parameters
        
        Returns:
            Response JSON data or None if all retries failed
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(
                    url, 
                    params=params, 
                    timeout=self.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.MAX_RETRIES})")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
        
        return None
    
    def fetch_top_works(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch top research works matching the search criteria.
        
        Args:
            criteria: Search criteria
        
        Returns:
            List of top works (papers)
        """
        logger.info(f"Fetching top {self.TOP_WORKS_COUNT} research works...")
        
        search_query = self.build_search_query(criteria)
        
        params = {
            'search': search_query,
            'per_page': self.TOP_WORKS_COUNT,
            'sort': 'cited_by_count:desc',
            'filter': 'primary_location.source.type:journal'
        }
        
        # Add email for polite pool (better rate limits)
        if self.email:
            params['mailto'] = self.email
        
        # Add open access filter if specified
        if criteria.get('openAccess') == 1:
            # Extend existing filter
            params['filter'] += ',is_oa:true'
        
        data = self.make_request_with_retry(self.WORKS_BASE_URL, params)
        
        if not data:
            logger.error("Failed to fetch works from OpenAlex")
            return []
        
        works = data.get('results', [])
        logger.info(f"Retrieved {len(works)} research works")
        return works
    
    def extract_journal_ids(self, works: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extract unique journal IDs and count their occurrences.
        
        Args:
            works: List of research works
        
        Returns:
            Dictionary mapping journal_id -> occurrence_count
        """
        journal_counts = {}
        
        for work in works:
            source = work.get('primary_location', {}).get('source', {})
            journal_id = source.get('id')
            
            if journal_id:
                journal_counts[journal_id] = journal_counts.get(journal_id, 0) + 1
        
        logger.info(f"Extracted {len(journal_counts)} unique journals")
        return journal_counts
    
    def fetch_journal_details(self, journal_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for journals from OpenAlex /sources endpoint.
        
        Args:
            journal_ids: List of OpenAlex journal IDs
        
        Returns:
            List of journal detail dictionaries
        """
        if not journal_ids:
            logger.warning("No journal IDs to fetch")
            return []
        
        logger.info(f"Fetching details for {len(journal_ids)} journals...")
        
        # Extract OpenAlex ID (remove URL prefix)
        clean_ids = [jid.replace('https://openalex.org/', '') for jid in journal_ids]
        
        # Build filter for multiple IDs
        ids_filter = 'ids.openalex:' + '|'.join(clean_ids)
        
        params = {
            'filter': ids_filter,
            'per_page': len(clean_ids)
        }
        
        if self.email:
            params['mailto'] = self.email
        
        data = self.make_request_with_retry(self.SOURCES_BASE_URL, params)
        
        if not data:
            logger.error("Failed to fetch journal details from OpenAlex")
            return []
        
        journals = data.get('results', [])
        logger.info(f"Retrieved details for {len(journals)} journals")
        return journals
    
    def calculate_journal_score(self, journal: Dict[str, Any], relevance_count: int) -> float:
        """
        Calculate comprehensive quality score for a journal.
        
        Scoring Breakdown:
        - Relevance (40%): How many times it appeared in top works
        - h-index (30%): Journal impact factor
        - Citations (20%): Total citation count
        - Open Access (10%): OA availability
        
        Args:
            journal: Journal data from OpenAlex
            relevance_count: Number of times journal appeared in top works
        
        Returns:
            Score from 0 to 100
        """
        score = 0.0
        
        # 1. Relevance Score (40 points max)
        # Normalize: 10+ appearances = full points
        max_relevance = 10
        relevance_score = min(relevance_count / max_relevance, 1.0) * self.WEIGHT_RELEVANCE
        score += relevance_score
        
        # 2. h-index Score (30 points max)
        # Top journals have h-index 100-200+
        h_index = journal.get('summary_stats', {}).get('h_index', 0)
        max_h_index = 200
        h_index_score = min(h_index / max_h_index, 1.0) * self.WEIGHT_H_INDEX
        score += h_index_score
        
        # 3. Citation Score (20 points max)
        # Normalize based on total citations
        cited_by_count = journal.get('cited_by_count', 0)
        max_citations = 100000  # Top journals have 100k+ citations
        citation_score = min(cited_by_count / max_citations, 1.0) * self.WEIGHT_CITATIONS
        score += citation_score
        
        # 4. Open Access Score (10 points)
        is_oa = journal.get('is_oa', False)
        is_in_doaj = journal.get('is_in_doaj', False)
        if is_oa or is_in_doaj:
            score += self.WEIGHT_OPEN_ACCESS
        
        return round(score, 2)
    
    def rank_journals(self, journals: List[Dict[str, Any]], 
                     journal_counts: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Rank journals by calculated score.
        
        Args:
            journals: List of journal details
            journal_counts: Dictionary of journal_id -> occurrence_count
        
        Returns:
            Sorted list of journals with scores
        """
        logger.info("Ranking journals by score...")
        
        scored_journals = []
        for journal in journals:
            journal_id = journal.get('id')
            relevance_count = journal_counts.get(journal_id, 0)
            
            # Calculate score
            score = self.calculate_journal_score(journal, relevance_count)
            
            # Add metadata
            journal['relevance_count'] = relevance_count
            journal['calculated_score'] = score
            scored_journals.append(journal)
        
        # Sort by score (descending)
        ranked = sorted(scored_journals, key=lambda x: x['calculated_score'], reverse=True)
        
        logger.info(f"Ranked {len(ranked)} journals")
        return ranked
    
    def format_journal_output(self, journal: Dict[str, Any], rank: int) -> Dict[str, Any]:
        """
        Format journal data for final output.
        
        Args:
            journal: Raw journal data from OpenAlex
            rank: Journal ranking (1, 2, 3, etc.)
        
        Returns:
            Formatted journal dictionary
        """
        return {
            "rank": rank,
            "journal_name": journal.get('display_name', 'N/A'),
            "issn": journal.get('issn', []),
            "issn_l": journal.get('issn_l', 'N/A'),
            "publisher": journal.get('host_organization_name', 'N/A'),
            "homepage_url": journal.get('homepage_url', 'N/A'),
            "h_index": journal.get('summary_stats', {}).get('h_index', 0),
            "i10_index": journal.get('summary_stats', {}).get('i10_index', 0),
            "cited_by_count": journal.get('cited_by_count', 0),
            "works_count": journal.get('works_count', 0),
            "is_open_access": journal.get('is_oa', False),
            "is_in_doaj": journal.get('is_in_doaj', False),
            "apc_usd": journal.get('apc_usd'),
            "societies": journal.get('societies', []),
            "relevance_count": journal.get('relevance_count', 0),
            "calculated_score": journal.get('calculated_score', 0.0),
            "openalex_id": journal.get('id', 'N/A'),
            "type": journal.get('type', 'journal')
        }
    
    def save_results(self, journals: List[Dict[str, Any]], 
                    output_file: str = 'journal_results.json'):
        """
        Save journal results to JSON file.
        
        Args:
            journals: List of formatted journals
            output_file: Output filename
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(journals, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    def print_results(self, journals: List[Dict[str, Any]]):
        """
        Print formatted journal results to console.
        
        Args:
            journals: List of formatted journals
        """
        print("\n" + "="*80)
        print(f"TOP {len(journals)} RESEARCH JOURNALS")
        print("="*80 + "\n")
        
        for journal in journals:
            print(f"{journal['rank']}. {journal['journal_name']}")
            print(f"   Publisher: {journal['publisher']}")
            print(f"   ISSN: {', '.join(journal['issn']) if journal['issn'] else 'N/A'}")
            print(f"   h-index: {journal['h_index']} | i10-index: {journal['i10_index']}")
            print(f"   Total Citations: {journal['cited_by_count']:,}")
            print(f"   Total Works: {journal['works_count']:,}")
            print(f"   Open Access: {'Yes' if journal['is_open_access'] else 'No'}")
            if journal['is_in_doaj']:
                print(f"   In DOAJ: Yes")
            if journal['apc_usd']:
                print(f"   APC: ${journal['apc_usd']:,.2f}")
            print(f"   Relevance: {journal['relevance_count']} works in top {self.TOP_WORKS_COUNT}")
            print(f"   Quality Score: {journal['calculated_score']:.2f}/100")
            print(f"   Homepage: {journal['homepage_url']}")
            print()
        
        print("="*80)
    
    def find_top_journals(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main method: Find and rank top journals for the given criteria.
        
        Two-step strategy:
        1. Fetch top works (papers) matching criteria
        2. Extract journals and rank by quality score
        
        Args:
            criteria: Search criteria from Vraj's refined output
        
        Returns:
            List of top journals (formatted)
        """
        # Validate criteria
        is_valid, errors = self.validate_criteria(criteria)
        if not is_valid:
            logger.error("Invalid search criteria:")
            for error in errors:
                logger.error(f"  - {error}")
            return []
        
        # Step 1: Fetch top research works
        works = self.fetch_top_works(criteria)
        if not works:
            logger.error("No works found")
            return []
        
        # Step 2: Extract unique journal IDs
        journal_counts = self.extract_journal_ids(works)
        if not journal_counts:
            logger.error("No journals extracted from works")
            return []
        
        # Step 3: Fetch journal details
        journal_ids = list(journal_counts.keys())
        journals = self.fetch_journal_details(journal_ids)
        if not journals:
            logger.error("Failed to fetch journal details")
            return []
        
        # Step 4: Rank journals by score
        ranked_journals = self.rank_journals(journals, journal_counts)
        
        # Step 5: Format top N journals
        top_journals = [
            self.format_journal_output(journal, rank)
            for rank, journal in enumerate(ranked_journals[:self.TOP_JOURNALS_COUNT], 1)
        ]
        
        return top_journals


def main():
    """Main execution function."""
    logger.info("Starting OpenAlex Journal Fetcher (Optimized)")
    logger.info("="*80)
    
    # Initialize fetcher
    fetcher = OpenAlexJournalFetcher()
    
    # Load search criteria from Vraj's output
    criteria = fetcher.load_search_criteria()
    if not criteria:
        logger.error("Failed to load search criteria. Exiting.")
        return
    
    # Display criteria
    logger.info("\nSearch Criteria:")
    logger.info(f"  Subject Area: {criteria.get('subjectArea', 'N/A')}")
    logger.info(f"  Keywords: {len(criteria.get('keywords', []))} keywords")
    logger.info(f"  Open Access: {'Free only' if criteria.get('openAccess') == 1 else 'Any (free + paid)'}")
    if 'acceptancePercentFrom' in criteria:
        logger.info(f"  Acceptance %: {criteria.get('acceptancePercentFrom')}-{criteria.get('acceptancePercentTo')}")
    
    # Find top journals
    logger.info("\n" + "-"*80)
    top_journals = fetcher.find_top_journals(criteria)
    
    if not top_journals:
        logger.error("No journals found. Please check your criteria or API connection.")
        return
    
    # Display results
    fetcher.print_results(top_journals)
    
    # Save results
    output_file = 'journal_results.json'
    fetcher.save_results(top_journals, output_file)
    
    logger.info(f"\n[SUCCESS] Found {len(top_journals)} top journals")
    logger.info(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
