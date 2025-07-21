"""
Gmail + Scraper Integration MCP Tools

MCP tool registrations for scraper tools that work with Gmail data.
These tools combine data extraction with scraping functionality.
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
def mcp_get_job_details_from_email(email_id: str):
    """
    Extract job URLs from a specific email and scrape complete job details.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of complete job data dictionaries with scraped details
    """
    return get_job_details_from_email(email_id)


@app.tool()
def mcp_scrape_jobs_from_email_urls(email_id: str, urls: List[str]):
    """
    Scrape job details from a list of URLs with email context.
    
    Args:
        email_id: Source Gmail message ID (for context)
        urls: List of LinkedIn job URLs to scrape
        
    Returns:
        List of scraped job data dictionaries
    """
    return scrape_jobs_from_email_urls(email_id, urls)


@app.tool()
def mcp_scrape_jobs_from_url_list(urls: List[str], context: Dict[str, Any] = None):
    """
    Scrape job details from a list of URLs with optional context.
    
    Args:
        urls: List of LinkedIn job URLs to scrape
        context: Optional context dictionary (e.g., source info)
        
    Returns:
        List of scraped job data dictionaries
    """
    return scrape_jobs_from_url_list(urls, context)


@app.tool()
def mcp_process_linkedin_emails(email_ids: List[str], max_jobs_per_email: int = 5):
    """
    Process multiple LinkedIn emails and extract all job details.
    
    Args:
        email_ids: List of Gmail message IDs
        max_jobs_per_email: Maximum number of jobs to scrape per email
        
    Returns:
        Dictionary with processed results summary and job details
    """
    return process_linkedin_emails(email_ids, max_jobs_per_email) 