"""
Scraper Tools Package

Tools that combine data extraction with scraping functionality.
These tools are designed to work with MCP and take necessary data as arguments.
"""

from .gmail_scraper import (
    get_job_details_from_email,
    scrape_jobs_from_email_urls,
    process_linkedin_emails
)

__all__ = [
    'get_job_details_from_email',
    'scrape_jobs_from_email_urls', 
    'process_linkedin_emails'
] 