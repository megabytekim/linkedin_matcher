"""Job Scraper Module for LinkedIn Job Matching.

This module provides web scraping functionality for:
- Scraping LinkedIn job pages with Playwright
- Extracting job details (title, company, location, description)
- Converting regular LinkedIn URLs to guest URLs
- Parsing HTML content with BeautifulSoup
"""

from .job_scraper import JobScraper

__version__ = "1.0.0"
__author__ = "LinkedIn Matcher Team"

__all__ = ["JobScraper"] 