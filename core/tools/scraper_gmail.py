"""
Gmail + Scraper Integration MCP Tools

Action-oriented MCP tools that combine Gmail data extraction with LinkedIn scraping.
These tools represent high-level agent capabilities for processing LinkedIn emails.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.server_app import app
from scraper_module.tools.gmail_scraper import (
    get_job_details_from_email,
    scrape_jobs_from_email_urls,
    scrape_jobs_from_url_list,
    process_linkedin_emails
)

@app.tool()
async def get_job_details_from_email(email_id: str):
    """
    Extract job URLs from a specific email and scrape complete job details.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of complete job data dictionaries with scraped details
    """
    from scraper_module.tools.gmail_scraper import get_job_details_from_email as get_details
    return get_details(email_id)

@app.tool()
async def scrape_jobs_from_email_urls(email_id: str, urls: List[str]):
    """
    Scrape job details from a list of URLs with email context.
    
    Args:
        email_id: Source Gmail message ID (for context)
        urls: List of LinkedIn job URLs to scrape
        
    Returns:
        List of scraped job data dictionaries
    """
    from scraper_module.tools.gmail_scraper import scrape_jobs_from_email_urls as scrape_from_email
    return scrape_from_email(email_id, urls)

@app.tool()
async def scrape_jobs_from_url_list(urls: List[str]):
    """
    Scrape job details from a list of LinkedIn URLs.
    
    Args:
        urls: List of LinkedIn job URLs to scrape
        
    Returns:
        List of scraped job data dictionaries
    """
    from scraper_module.tools.gmail_scraper import scrape_jobs_from_url_list as scrape_urls
    return scrape_urls(urls)

@app.tool()
async def process_linkedin_emails(query: str = "from:linkedin.com", max_results: int = 5, max_content_length: int = 2000):
    """
    Complete workflow: Find LinkedIn emails, extract URLs, scrape job details.
    
    Args:
        query: Gmail search query for LinkedIn emails
        max_results: Maximum number of emails to process
        max_content_length: Maximum content length for job descriptions
        
    Returns:
        Dictionary with email data and scraped job details
    """
    from scraper_module.tools.gmail_scraper import process_linkedin_emails as process_emails
    return process_emails(query, max_results, max_content_length) 