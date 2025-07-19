"""
Gmail Tools for LinkedIn Job Scraper

Pure functions for Gmail operations that are registered with the main MCP server.
No FastMCP instance is created here - tools are registered on the main app.
"""

from gmail_module.gmail_api import GmailAPI
from core.server_app import app

def list_emails(query: str = "from:linkedin.com", max_results: int = 10):
    """
    List Gmail messages matching the query.
    
    Args:
        query: Gmail search query (e.g., "from:linkedin.com", "subject:job")
        max_results: Maximum number of messages to return (1-50)
        
    Returns:
        List of message dictionaries with id, subject, from, date, snippet
    """
    gmail = GmailAPI()
    return gmail.list_messages(query, max_results)

def extract_job_urls(email_id: str):
    """
    Extract LinkedIn job URLs from a specific email.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of dictionaries with 'url' and 'link_text' keys
    """
    gmail = GmailAPI()
    return gmail.extract_job_urls(email_id)

def get_message_content(email_id: str):
    """
    Get the full text content of a Gmail message.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        Plain text content of the message or None if failed
    """
    gmail = GmailAPI()
    return gmail.get_message_content(email_id)

def add_label(email_id: str, label: str):
    """
    Add a label to a Gmail message.
    
    Args:
        email_id: Gmail message ID
        label: Name of the label to add
        
    Returns:
        True if successful, False otherwise
    """
    gmail = GmailAPI()
    return gmail.add_label(email_id, label)

def get_job_details_from_email(email_id: str):
    """
    Extract job URLs from email and scrape complete job details.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of complete job data dictionaries with scraped details
    """
    from core.tools.scraper import scrape_job
    
    # Get job URLs from email
    job_urls = extract_job_urls(email_id)
    
    # Scrape each job URL
    job_details = []
    for url_info in job_urls:
        try:
            job_data = scrape_job(url_info['url'])
            if job_data:
                job_details.append(job_data)
        except Exception as e:
            print(f"Failed to scrape {url_info['url']}: {e}")
    
    return job_details

# Register tools with the main MCP server
@app.tool()
def mcp_list_emails(query: str = "from:linkedin.com", max_results: int = 10):
    """List Gmail messages matching the query."""
    return list_emails(query, max_results)

@app.tool()
def mcp_extract_job_urls(email_id: str):
    """Extract LinkedIn job URLs from a specific email."""
    return extract_job_urls(email_id)

@app.tool()
def mcp_get_message_content(email_id: str):
    """Get full content of an email."""
    return get_message_content(email_id)

@app.tool()
def mcp_add_label(email_id: str, label: str):
    """Apply a label to a Gmail message."""
    return add_label(email_id, label)

@app.tool()
def mcp_get_job_details_from_email(email_id: str):
    """Extract job URLs from email and scrape complete job details."""
    return get_job_details_from_email(email_id) 