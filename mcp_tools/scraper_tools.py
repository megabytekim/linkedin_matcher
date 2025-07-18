"""
MCP Tools for LinkedIn Job Scraping

This module contains FastMCP tool implementations for LinkedIn scraping:
- scrape_job: Scrape a single LinkedIn job
- scrape_multiple_jobs: Batch scrape multiple job URLs
- convert_to_guest_url: Convert LinkedIn URLs to guest URLs
- validate_linkedin_url: Validate LinkedIn job URLs
"""

from fastmcp import FastMCP
from scraper_module.job_scraper import JobScraper, scrape_job_page, scrape_multiple_jobs as scraper_scrape_multiple_jobs

app = FastMCP("LinkedIn Scraper Tools")

@app.tool()
def scrape_job(url: str, max_content_length: int = 2000):
    """
    Scrape a single LinkedIn job posting.
    
    Args:
        url: LinkedIn job URL to scrape
        max_content_length: Maximum length for description content
        
    Returns:
        Dictionary with job information (title, company, location, description, etc.) or None if failed
    """
    return scrape_job_page(url, max_content_length)

@app.tool()
def scrape_multiple_jobs(urls: list[str], max_content_length: int = 1500):
    """
    Scrape multiple LinkedIn job postings with rate limiting.
    
    Args:
        urls: List of LinkedIn job URLs to scrape
        max_content_length: Maximum length for description content
        
    Returns:
        List of job data dictionaries
    """
    return scraper_scrape_multiple_jobs(urls, max_content_length)

@app.tool()
def convert_to_guest_url(linkedin_url: str):
    """
    Convert LinkedIn job URL to guest URL (no login required).
    
    Args:
        linkedin_url: Original LinkedIn job URL
        
    Returns:
        Guest URL string that can be accessed without LinkedIn login
    """
    scraper = JobScraper()
    return scraper._convert_to_guest_url(linkedin_url)

@app.tool()
def validate_linkedin_url(url: str):
    """
    Validate if URL is a valid LinkedIn job URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid LinkedIn job URL, False otherwise
    """
    scraper = JobScraper()
    return scraper.validate_linkedin_url(url)

@app.tool()
def get_job_summary(url: str):
    """
    Get quick summary of job posting (title, company, location only).
    
    Args:
        url: LinkedIn job URL
        
    Returns:
        Dictionary with basic job info or None if failed
    """
    # Use scrape_job_page but limit content length for faster processing
    job_data = scrape_job_page(url, max_content_length=500)
    if job_data:
        # Return only essential fields for quick summary
        return {
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'location': job_data.get('location', ''),
            'url': job_data.get('url', url),
            'guest_url': job_data.get('guest_url', ''),
            'scraped_at': job_data.get('scraped_at', '')
        }
    return None 