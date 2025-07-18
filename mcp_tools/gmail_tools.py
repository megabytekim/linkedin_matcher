"""
MCP Tools for Gmail Integration

This module contains pure Python functions for Gmail functionality:
- list_emails: List and search Gmail messages
- extract_job_urls: Extract LinkedIn job URLs from emails
- label_email: Apply labels to processed emails
- get_email_content: Retrieve full email content
- get_job_details_from_email: Complete email to job data workflow
"""

from gmail_module.gmail_api import GmailAPI

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

def get_email_content(email_id: str):
    """
    Get full content of an email.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        Plain text content of the email or None if failed
    """
    gmail = GmailAPI()
    return gmail.get_email_content(email_id)

def label_email(email_id: str, label: str):
    """
    Apply a label to a Gmail message.
    
    Args:
        email_id: Gmail message ID
        label: Label name to apply (e.g., "PROCESSED", "JOB_FOUND")
        
    Returns:
        True if successful, False otherwise
    """
    gmail = GmailAPI()
    return gmail.label_email(email_id, label)

def get_job_details_from_email(email_id: str):
    """
    Extract job URLs from email and scrape complete job details.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of complete job data dictionaries with scraped details
    """
    from scraper_module.job_scraper import scrape_job_page
    
    # Get job URLs from email
    job_urls = extract_job_urls(email_id)
    
    # Scrape each job URL
    job_details = []
    for url_info in job_urls:
        try:
            job_data = scrape_job_page(url_info['url'])
            if job_data:
                job_details.append(job_data)
        except Exception as e:
            print(f"Failed to scrape {url_info['url']}: {e}")
    
    return job_details 