"""
MCP Tools for Gmail Integration

This module contains FastMCP tool implementations for Gmail functionality:
- list_emails: List and search Gmail messages
- extract_job_urls: Extract LinkedIn job URLs from emails
- label_emails: Apply labels to processed emails
- get_email_content: Retrieve full email content
"""

from fastmcp import FastMCP
from gmail_module.gmail_api import GmailAPI

app = FastMCP("Gmail Tools")

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
    gmail = GmailAPI()
    return gmail.list_messages(query, max_results)

@app.tool()
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

@app.tool()
def get_email_content(email_id: str):
    """
    Get full content of an email.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        Plain text content of the email or None if failed
    """
    gmail = GmailAPI()
    return gmail.get_message_content(email_id)

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
    gmail = GmailAPI()
    return gmail.add_label(email_id, label)

@app.tool()
def get_job_details_from_email(email_id: str):
    """
    Extract job URLs from email and scrape complete job details.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of complete job data dictionaries with scraped details
    """
    gmail = GmailAPI()
    return gmail.get_job_details_from_email(email_id) 