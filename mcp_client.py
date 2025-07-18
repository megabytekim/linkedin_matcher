"""
FastMCP Client for LinkedIn Job Scraper

This file contains the Model Context Protocol client implementation
for integrating Gmail and LinkedIn scraper functionality as MCP tools.
"""

from fastmcp import FastMCP

# Create main MCP application
app = FastMCP("LinkedIn Job Scraper")

# Gmail tools
@app.tool()
def list_emails(query: str = "from:linkedin.com", max_results: int = 10):
    """
    List Gmail messages matching the query.
    
    Args:
        query: Gmail search query (e.g., "from:linkedin.com", "subject:job")
        max_results: Maximum number of messages to return (1-50)
        
    Returns:
        List of message dictionaries with id, subject, from, date, snippet
    """
    from mcp_tools.gmail_tools import list_emails as gmail_list_emails
    return gmail_list_emails(query, max_results)

@app.tool()
def extract_job_urls(email_id: str):
    """
    Extract LinkedIn job URLs from a specific email.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of dictionaries with 'url' and 'link_text' keys
    """
    from mcp_tools.gmail_tools import extract_job_urls as gmail_extract_urls
    return gmail_extract_urls(email_id)

@app.tool()
def get_email_content(email_id: str):
    """
    Get full content of an email.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        Plain text content of the email or None if failed
    """
    from mcp_tools.gmail_tools import get_email_content as gmail_get_content
    return gmail_get_content(email_id)

@app.tool()
def label_email(email_id: str, label: str):
    """
    Apply a label to an email.
    
    Args:
        email_id: Gmail message ID
        label: Name of the label to add
        
    Returns:
        True if successful, False otherwise
    """
    from mcp_tools.gmail_tools import label_email as gmail_label_email
    return gmail_label_email(email_id, label)

@app.tool()
def get_job_details_from_email(email_id: str):
    """
    Extract job URLs from email and scrape complete job details.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of complete job data dictionaries with scraped details
    """
    from mcp_tools.gmail_tools import get_job_details_from_email as gmail_get_job_details
    return gmail_get_job_details(email_id)

# Scraper tools
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
    from mcp_tools.scraper_tools import scrape_job as scraper_scrape_job
    return scraper_scrape_job(url, max_content_length)

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
    from mcp_tools.scraper_tools import scrape_multiple_jobs as scraper_scrape_multiple
    return scraper_scrape_multiple(urls, max_content_length)

@app.tool()
def convert_to_guest_url(linkedin_url: str):
    """
    Convert LinkedIn job URL to guest URL (no login required).
    
    Args:
        linkedin_url: Original LinkedIn job URL
        
    Returns:
        Guest URL string that can be accessed without LinkedIn login
    """
    from mcp_tools.scraper_tools import convert_to_guest_url as scraper_convert_url
    return scraper_convert_url(linkedin_url)

@app.tool()
def validate_linkedin_url(url: str):
    """
    Validate if URL is a valid LinkedIn job URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid LinkedIn job URL, False otherwise
    """
    from mcp_tools.scraper_tools import validate_linkedin_url as scraper_validate_url
    return scraper_validate_url(url)

@app.tool()
def get_job_summary(url: str):
    """
    Get quick summary of job posting (title, company, location only).
    
    Args:
        url: LinkedIn job URL
        
    Returns:
        Dictionary with basic job info or None if failed
    """
    from mcp_tools.scraper_tools import get_job_summary as scraper_get_summary
    return scraper_get_summary(url)

# Convenience workflow tools
@app.tool()
def full_workflow(query: str = "from:linkedin.com", max_emails: int = 5, max_jobs: int = 10):
    """
    Complete workflow: Search emails → Extract URLs → Scrape jobs.
    
    Args:
        query: Gmail search query for finding job emails
        max_emails: Maximum emails to process
        max_jobs: Maximum jobs to scrape
        
    Returns:
        Dictionary with emails found, URLs extracted, and jobs scraped
    """
    # Import directly to avoid recursion
    from mcp_tools.gmail_tools import list_emails as gmail_list_emails
    from mcp_tools.gmail_tools import extract_job_urls as gmail_extract_urls  
    from scraper_module.job_scraper import scrape_multiple_jobs as direct_scrape_multiple
    
    # Step 1: Find emails
    emails = gmail_list_emails(query, max_emails)
    
    # Step 2: Extract URLs from all emails
    all_urls = []
    for email in emails[:max_emails]:
        urls = gmail_extract_urls(email['id'])
        all_urls.extend([url_info['url'] for url_info in urls])
    
    # Step 3: Scrape jobs (limit to max_jobs)
    urls_to_scrape = all_urls[:max_jobs]
    job_results = direct_scrape_multiple(urls_to_scrape) if urls_to_scrape else []
    
    return {
        'emails_found': len(emails),
        'urls_extracted': len(all_urls),
        'jobs_scraped': len(job_results),
        'job_data': job_results,
        'summary': f"Found {len(emails)} emails, extracted {len(all_urls)} URLs, scraped {len(job_results)} jobs"
    }

if __name__ == "__main__":
    # Run the MCP server
    print("🚀 Starting LinkedIn Job Scraper MCP Server...")
    print("📧 Gmail Tools: list_emails, extract_job_urls, get_email_content, label_email")
    print("🌐 Scraper Tools: scrape_job, scrape_multiple_jobs, convert_to_guest_url, validate_linkedin_url")
    print("🔄 Workflow Tool: full_workflow")
    
    app.run() 