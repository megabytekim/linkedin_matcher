"""
LinkedIn Scraper Tools for LinkedIn Job Scraper

Action-oriented MCP tools for LinkedIn job scraping operations.
These tools represent specific agent capabilities for web scraping.
"""

from scraper_module.job_scraper import JobScraper
from core.server_app import app

@app.tool()
async def scrape_job(url: str, max_content_length: int = 2000):
    """
    Scrape LinkedIn job page for detailed information.
    
    Args:
        url: LinkedIn job URL to scrape
        max_content_length: Maximum length for description content
        
    Returns:
        Dictionary with job information or None if failed
    """
    try:
        async with JobScraper() as scraper:
            return await scraper.scrape_job_page(url, max_content_length)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

@app.tool()
async def validate_job_url(url: str):
    """
    Validate if a URL is a LinkedIn job URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Boolean indicating if URL is valid LinkedIn job URL
    """
    try:
        async with JobScraper() as scraper:
            return scraper.is_linkedin_job_url(url)
    except Exception as e:
        print(f"Error validating URL {url}: {e}")
        return False

@app.tool()
async def scrape_multiple_jobs(urls: list, max_content_length: int = 2000):
    """
    Scrape multiple LinkedIn job pages efficiently.
    
    Args:
        urls: List of LinkedIn job URLs to scrape
        max_content_length: Maximum length for description content
        
    Returns:
        List of job dictionaries (None for failed scrapes)
    """
    try:
        async with JobScraper() as scraper:
            results = []
            for url in urls:
                try:
                    job_data = await scraper.scrape_job_page(url, max_content_length)
                    results.append(job_data)
                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    results.append(None)
            return results
    except Exception as e:
        print(f"Error in batch scraping: {e}")
        return [None] * len(urls) 