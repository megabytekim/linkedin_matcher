"""
Gmail Tools for LinkedIn Job Scraper

Pure functions for Gmail operations that are registered with the main MCP server.
No FastMCP instance is created here - tools are registered on the main app.

These tools focus on pure data extraction from Gmail without scraping dependencies.
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

# Register tools with the main MCP server
@app.tool()
def mcp_list_emails(query: str = "from:linkedin.com", max_results: int = 10):
    """List Gmail messages matching the query."""
    emails = list_emails(query, max_results)
    import json
    # 한글이 깨지지 않도록 ensure_ascii=False로 직렬화
    return [json.dumps(email, ensure_ascii=False) for email in emails]

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