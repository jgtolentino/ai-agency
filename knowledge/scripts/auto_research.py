#!/usr/bin/env python3
"""
Deep Research Automation for Odoo Expertise
Auto-crawls OCA GitHub, Reddit r/odoo, and Odoo forums

Purpose: Feed knowledge base with latest patterns, issues, and solutions
Output: Structured citations following citation_template.md format
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import requests
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QualityScorer:
    """Calculate quality scores for research sources"""

    # Base quality scores (from deep_research_odoo.md)
    QUALITY_SCORES = {
        'official_odoo_docs': 100,
        'oca_maintainer_response': 95,
        'oca_repository_code': 90,
        'stackoverflow_accepted_20plus': 85,
        'reddit_10plus_upvotes_solved': 75,
        'stackoverflow_accepted_10_19': 70,
        'forum_official_response': 70,
        'reddit_5_9_upvotes': 60,
        'stackoverflow_no_accept_10plus': 50,
    }

    # Recency bonuses
    RECENCY_BONUS = {
        2025: 20,
        2024: 15,
        2023: 10,
        2022: 0,
    }

    # Alignment bonuses
    ALIGNMENT_BONUS = {
        'oca_compliant': 15,
        'self_hosted_focus': 10,
        'version_16_17_19': 10,
        'proprietary_only': -30,
    }

    MIN_ACCEPTABLE_SCORE = 60

    @staticmethod
    def calculate(source_type: str, date: datetime, upvotes: int = 0,
                  accepted: bool = False, oca_aligned: bool = False) -> int:
        """Calculate total quality score for a source"""

        # Base score
        score = 0
        if source_type == 'oca':
            score = QualityScorer.QUALITY_SCORES['oca_repository_code']
        elif source_type == 'reddit':
            if upvotes >= 10:
                score = QualityScorer.QUALITY_SCORES['reddit_10plus_upvotes_solved']
            elif upvotes >= 5:
                score = QualityScorer.QUALITY_SCORES['reddit_5_9_upvotes']
        elif source_type == 'stackoverflow':
            if accepted and upvotes >= 20:
                score = QualityScorer.QUALITY_SCORES['stackoverflow_accepted_20plus']
            elif accepted and upvotes >= 10:
                score = QualityScorer.QUALITY_SCORES['stackoverflow_accepted_10_19']
            elif upvotes >= 10:
                score = QualityScorer.QUALITY_SCORES['stackoverflow_no_accept_10plus']
        elif source_type == 'forum':
            score = QualityScorer.QUALITY_SCORES['forum_official_response']
        elif source_type == 'official':
            score = QualityScorer.QUALITY_SCORES['official_odoo_docs']

        # Recency bonus
        year = date.year
        if year >= 2021:
            recency = QualityScorer.RECENCY_BONUS.get(year, -20)
            score += recency

        # Alignment bonus
        if oca_aligned:
            score += QualityScorer.ALIGNMENT_BONUS['oca_compliant']

        return score

    @staticmethod
    def is_acceptable(score: int) -> bool:
        """Check if score meets minimum threshold"""
        return score >= QualityScorer.MIN_ACCEPTABLE_SCORE


class OCAGitHubCrawler:
    """Crawl OCA GitHub repositories for patterns and code examples"""

    BASE_URL = "https://api.github.com"

    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token or os.environ.get('GITHUB_TOKEN')
        self.headers = {}
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        self.headers['Accept'] = 'application/vnd.github.v3+json'

    def search_code(self, query: str, repo: str = None, limit: int = 10) -> List[Dict]:
        """Search OCA code for patterns"""

        search_query = f"org:OCA {query}"
        if repo:
            search_query = f"repo:OCA/{repo} {query}"

        url = f"{self.BASE_URL}/search/code"
        params = {'q': search_query, 'per_page': limit}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            results = response.json()

            items = []
            for item in results.get('items', []):
                items.append({
                    'title': f"OCA Pattern: {item['name']}",
                    'url': item['html_url'],
                    'path': item['path'],
                    'repo': item['repository']['full_name'],
                    'source_type': 'oca',
                    'date': datetime.now(),  # GitHub code search doesn't provide dates
                })

            logger.info(f"Found {len(items)} OCA code results for: {query}")
            return items

        except requests.RequestException as e:
            logger.error(f"GitHub API error: {e}")
            return []

    def get_file_content(self, url: str) -> Optional[str]:
        """Fetch file content from GitHub"""

        # Convert HTML URL to raw URL
        raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')

        try:
            response = requests.get(raw_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching file content: {e}")
            return None

    def extract_snippet(self, content: str, max_lines: int = 2) -> str:
        """Extract relevant code snippet (≤2 lines)"""

        if not content:
            return ""

        lines = content.split('\n')

        # Look for key patterns
        patterns = [
            r'@api\.depends',
            r'def _compute',
            r'@api\.constrains',
            r'def create\(',
            r'def write\(',
            r'class.*\(models\.',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    # Return this line and next (max 2 lines)
                    snippet_lines = lines[i:min(i+max_lines, len(lines))]
                    return '\n'.join(snippet_lines).strip()

        # Fallback: return first non-empty lines
        non_empty = [l.strip() for l in lines if l.strip()]
        return '\n'.join(non_empty[:max_lines])


class RedditCrawler:
    """Crawl Reddit r/odoo for community solutions"""

    BASE_URL = "https://www.reddit.com"

    def __init__(self):
        self.headers = {
            'User-Agent': 'Cline Deep Research Bot 1.0'
        }

    def search(self, query: str, min_upvotes: int = 5, limit: int = 10) -> List[Dict]:
        """Search r/odoo subreddit"""

        url = f"{self.BASE_URL}/r/odoo/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',
            'sort': 'relevance',
            'limit': limit,
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            items = []
            for post in data.get('data', {}).get('children', []):
                post_data = post['data']
                upvotes = post_data.get('ups', 0)

                # Filter by upvotes
                if upvotes < min_upvotes:
                    continue

                items.append({
                    'title': post_data['title'],
                    'url': f"{self.BASE_URL}{post_data['permalink']}",
                    'upvotes': upvotes,
                    'created': datetime.fromtimestamp(post_data['created_utc']),
                    'source_type': 'reddit',
                    'selftext': post_data.get('selftext', '')[:200],  # First 200 chars
                })

            logger.info(f"Found {len(items)} Reddit results for: {query}")
            return items

        except requests.RequestException as e:
            logger.error(f"Reddit API error: {e}")
            return []


class StackOverflowCrawler:
    """Crawl Stack Overflow for Odoo solutions"""

    BASE_URL = "https://api.stackexchange.com/2.3"

    def search(self, query: str, min_upvotes: int = 10, limit: int = 10) -> List[Dict]:
        """Search Stack Overflow [odoo] tag"""

        url = f"{self.BASE_URL}/search/advanced"
        params = {
            'order': 'desc',
            'sort': 'votes',
            'tagged': 'odoo',
            'q': query,
            'site': 'stackoverflow',
            'pagesize': limit,
            'filter': 'withbody',
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            items = []
            for item in data.get('items', []):
                upvotes = item.get('score', 0)

                # Filter by upvotes
                if upvotes < min_upvotes:
                    continue

                items.append({
                    'title': item['title'],
                    'url': item['link'],
                    'upvotes': upvotes,
                    'created': datetime.fromtimestamp(item['creation_date']),
                    'accepted': item.get('is_answered', False),
                    'source_type': 'stackoverflow',
                    'body_preview': item.get('body', '')[:200],
                })

            logger.info(f"Found {len(items)} Stack Overflow results for: {query}")
            return items

        except requests.RequestException as e:
            logger.error(f"Stack Overflow API error: {e}")
            return []


class CitationFormatter:
    """Format research results as citations following citation_template.md"""

    @staticmethod
    def format(item: Dict, snippet: str = "", takeaway: str = "",
               application: List[str] = None, tags: List[str] = None) -> str:
        """Format item as markdown citation"""

        # Calculate quality score
        score = QualityScorer.calculate(
            source_type=item['source_type'],
            date=item.get('created', item.get('date', datetime.now())),
            upvotes=item.get('upvotes', 0),
            accepted=item.get('accepted', False),
            oca_aligned=item['source_type'] == 'oca'
        )

        # Format date
        date_str = item.get('created', item.get('date', datetime.now())).strftime('%Y-%m-%d')

        # Default values
        application = application or ['odoo-module-dev']
        tags = tags or []

        # Build citation
        citation = f"""## {item['title']}

- **Link**: {item['url']}
- **Date/Version**: {date_str}
- **Source Type**: {item['source_type'].title().replace('_', ' ')}
- **Quality Score**: {score}
- **Takeaway**: {takeaway or 'Manual review required'}
- **Snippet**: {snippet or 'See link for details'}
- **Application**: {', '.join(application)}
- **Tags**: {', '.join(tags)}

"""
        return citation


class ResearchAutomation:
    """Main research automation orchestrator"""

    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.oca_crawler = OCAGitHubCrawler()
        self.reddit_crawler = RedditCrawler()
        self.stackoverflow_crawler = StackOverflowCrawler()

        # Load query sets from playbook
        self.queries = self._load_queries()

    def _load_queries(self) -> Dict:
        """Load query sets from deep_research_odoo.md"""

        # Default queries if playbook not found
        return {
            'module_dev': {
                'oca': [
                    '@api.depends computed field',
                    'record rule domain multi-company',
                    'pytest-odoo TransactionCase',
                ],
                'reddit': [
                    'OCA module best practices',
                    'computed field cache',
                ],
                'stackoverflow': [
                    '@api.depends computed field',
                    'record rule performance',
                ],
            },
            'docker': {
                'reddit': [
                    'docker wkhtmltopdf fonts',
                    'docker compose odoo postgres',
                ],
                'stackoverflow': [
                    'docker odoo wkhtmltopdf',
                    'docker odoo non-root',
                ],
            }
        }

    def run_research(self, domain: str = 'module_dev', max_results: int = 5) -> List[Dict]:
        """Run parallel research queries"""

        logger.info(f"Starting research for domain: {domain}")

        queries = self.queries.get(domain, {})
        results = []

        # OCA GitHub queries
        for query in queries.get('oca', []):
            items = self.oca_crawler.search_code(query, limit=3)
            for item in items[:max_results]:
                # Fetch content and extract snippet
                content = self.oca_crawler.get_file_content(item['url'])
                snippet = self.oca_crawler.extract_snippet(content)
                item['snippet'] = snippet
                results.append(item)

        # Reddit queries
        for query in queries.get('reddit', []):
            items = self.reddit_crawler.search(query, min_upvotes=5, limit=3)
            results.extend(items[:max_results])

        # Stack Overflow queries (limit in test mode to avoid rate limits)
        if not self.test_mode:
            for query in queries.get('stackoverflow', []):
                items = self.stackoverflow_crawler.search(query, min_upvotes=10, limit=3)
                results.extend(items[:max_results])

        logger.info(f"Research complete. Found {len(results)} total results")
        return results

    def generate_citations(self, results: List[Dict]) -> str:
        """Generate markdown citations from results"""

        citations = []

        for item in results:
            # Auto-generate takeaway based on source type
            takeaway = self._generate_takeaway(item)

            # Auto-tag based on content
            tags = self._generate_tags(item)

            # Determine application
            application = self._determine_application(item)

            # Format citation
            citation = CitationFormatter.format(
                item,
                snippet=item.get('snippet', ''),
                takeaway=takeaway,
                application=application,
                tags=tags
            )

            citations.append(citation)

        return '\n'.join(citations)

    def _generate_takeaway(self, item: Dict) -> str:
        """Auto-generate takeaway from item content"""

        if item['source_type'] == 'oca':
            return f"OCA pattern from {item.get('repo', 'repository')} - review code for implementation details"
        elif item['source_type'] == 'reddit':
            preview = item.get('selftext', '')
            if preview:
                return preview[:100] + '...'
            return "Community solution - see discussion for details"
        elif item['source_type'] == 'stackoverflow':
            preview = item.get('body_preview', '')
            if preview:
                return preview[:100] + '...'
            return f"{item.get('upvotes', 0)} upvotes - see answer for solution"

        return "Manual review required"

    def _generate_tags(self, item: Dict) -> List[str]:
        """Auto-generate tags from item content"""

        tags = []

        # Extract from title
        title_lower = item['title'].lower()

        keyword_map = {
            'computed': 'computed-field',
            'api.depends': 'api-depends',
            'record rule': 'record-rules',
            'security': 'security',
            'performance': 'performance',
            'docker': 'docker',
            'wkhtmltopdf': 'wkhtmltopdf',
            'test': 'testing',
            'migration': 'migration',
            'orm': 'orm',
        }

        for keyword, tag in keyword_map.items():
            if keyword in title_lower:
                tags.append(tag)

        # Add source type as tag
        tags.append(item['source_type'])

        return tags

    def _determine_application(self, item: Dict) -> List[str]:
        """Determine which skills this applies to"""

        applications = []

        title_lower = item['title'].lower()

        # Module development
        if any(k in title_lower for k in ['orm', 'model', 'computed', 'api', 'security']):
            applications.append('odoo-module-dev')

        # Docker
        if any(k in title_lower for k in ['docker', 'container', 'wkhtmltopdf']):
            applications.append('odoo-docker-claude')

        # Default
        if not applications:
            applications.append('odoo-module-dev')

        return applications

    def save_to_daily_note(self, citations: str, output_dir: Path = None) -> Path:
        """Save citations to daily note"""

        if output_dir is None:
            # Default to knowledge/notes
            output_dir = Path(__file__).parent.parent / 'notes'

        output_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime('%Y-%m-%d')
        note_path = output_dir / f"{today}.md"

        # Create header if new file
        if not note_path.exists():
            header = f"""# Daily Research Notes - {today}

**Auto-generated research findings**

---

"""
            note_path.write_text(header)

        # Append citations
        with open(note_path, 'a') as f:
            f.write(citations)

        logger.info(f"Saved citations to: {note_path}")
        return note_path


def main():
    parser = argparse.ArgumentParser(
        description='Auto-research Odoo knowledge from OCA, Reddit, and Stack Overflow'
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode (limited queries, no Stack Overflow to avoid rate limits)'
    )
    parser.add_argument(
        '--domain',
        default='module_dev',
        choices=['module_dev', 'docker', 'studio', 'odoo_sh'],
        help='Research domain focus'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=5,
        help='Maximum results per query'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output directory for daily notes (default: knowledge/notes/)'
    )

    args = parser.parse_args()

    # Run research
    automation = ResearchAutomation(test_mode=args.test_mode)
    results = automation.run_research(domain=args.domain, max_results=args.max_results)

    # Filter by quality score
    filtered_results = [
        r for r in results
        if QualityScorer.is_acceptable(
            QualityScorer.calculate(
                r['source_type'],
                r.get('created', r.get('date', datetime.now())),
                r.get('upvotes', 0),
                r.get('accepted', False),
                r['source_type'] == 'oca'
            )
        )
    ]

    logger.info(f"Filtered to {len(filtered_results)} high-quality results")

    if len(filtered_results) < 5:
        logger.warning("Less than 5 citations generated - consider broadening search")

    # Generate citations
    citations = automation.generate_citations(filtered_results)

    # Save to daily note
    note_path = automation.save_to_daily_note(citations, args.output)

    print(f"\n✅ Research complete!")
    print(f"Generated {len(filtered_results)} citations")
    print(f"Saved to: {note_path}")

    if args.test_mode:
        print("\n📋 Sample citation:")
        print(citations.split('\n\n')[0] if citations else "No citations generated")

    return 0 if len(filtered_results) >= 5 else 1


if __name__ == '__main__':
    sys.exit(main())
