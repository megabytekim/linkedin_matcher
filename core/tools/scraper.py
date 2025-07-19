"""
LinkedIn Scraper Tools for LinkedIn Job Scraper

Pure functions for LinkedIn scraping operations that are registered with the main MCP server.
No FastMCP instance is created here - tools are registered on the main app.
"""

from scraper_module.job_scraper import JobScraper
from core.server_app import app

async def scrape_job_async(url: str, max_content_length: int = 2000):
    """
    Async-compatible scrape job function.
    
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

def scrape_job(url: str, max_content_length: int = 2000):
    """
    Synchronous scrape job function for backwards compatibility.
    
    Args:
        url: LinkedIn job URL to scrape
        max_content_length: Maximum length for description content
        
    Returns:
        Dictionary with job information or None if failed
    """
    import asyncio
    try:
        # Check if we're in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, can't use asyncio.run()
            # Return a placeholder for now
            return {
                'url': url,
                'error': 'Cannot scrape from async context - use scrape_job_async instead',
                'title': 'Scraping Error',
                'company': 'N/A',
                'location': 'N/A'
            }
        except RuntimeError:
            # No event loop running, safe to use asyncio.run()
            return asyncio.run(scrape_job_async(url, max_content_length))
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def scrape_multiple_jobs(urls: list[str], max_content_length: int = 1500):
    """
    Scrape multiple LinkedIn job postings with rate limiting.
    
    Args:
        urls: List of LinkedIn job URLs to scrape
        max_content_length: Maximum length for description content
        
    Returns:
        List of job data dictionaries
    """
    results = []
    for url in urls:
        result = scrape_job(url, max_content_length)
        if result:
            results.append(result)
    return results

def convert_to_guest_url(url: str):
    """
    Convert a LinkedIn job URL to guest URL (viewable without login).
    
    Args:
        url: LinkedIn job URL
        
    Returns:
        Guest URL string that can be accessed without LinkedIn login
    """
    scraper = JobScraper()
    return scraper._convert_to_guest_url(url)

def validate_linkedin_url(url: str):
    """
    Validate if a URL is a valid LinkedIn job URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid LinkedIn job URL, False otherwise
    """
    scraper = JobScraper()
    return scraper.validate_linkedin_url(url)

def get_job_summary(url: str):
    """
    Get quick summary of job posting (title, company, location only).
    
    Args:
        url: LinkedIn job URL
        
    Returns:
        Dictionary with basic job info or None if failed
    """
    # Use guest URL conversion for faster processing
    guest_url = convert_to_guest_url(url)
    if guest_url:
        return scrape_job(guest_url, max_content_length=500)
    return None

# Register tools with the main MCP server
@app.tool()
def mcp_scrape_job(url: str, max_content_length: int = 2000):
    """Scrape a single LinkedIn job posting."""
    return scrape_job(url, max_content_length)

@app.tool()
def mcp_scrape_multiple_jobs(urls: list[str], max_content_length: int = 1500):
    """Scrape multiple LinkedIn job postings with rate limiting."""
    return scrape_multiple_jobs(urls, max_content_length)

@app.tool()
def mcp_convert_to_guest_url(url: str):
    """Convert a LinkedIn job URL to guest URL (viewable without login)."""
    return convert_to_guest_url(url)

@app.tool()
def mcp_validate_linkedin_url(url: str):
    """Validate if a URL is a valid LinkedIn job URL."""
    return validate_linkedin_url(url)

@app.tool()
def mcp_get_job_summary(url: str):
    """Get quick summary of job posting (title, company, location only)."""
    return get_job_summary(url) 