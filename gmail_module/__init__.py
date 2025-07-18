"""Gmail Module for LinkedIn Job Matching.

This module provides Gmail API functionality for:
- Authenticating with Gmail
- Listing and searching emails
- Extracting job URLs from LinkedIn emails
- Scraping job details using Playwright
- Managing email labels
"""

from .gmail_api import GmailAPI

__version__ = "1.0.0"
__author__ = "LinkedIn Matcher Team"

__all__ = ["GmailAPI"] 