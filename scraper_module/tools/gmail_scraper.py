"""
Gmail + Scraper Integration Tools

Tools that combine Gmail data extraction with scraping functionality.
These tools take specific data as arguments and don't directly depend on Gmail API calls.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.tools.scraper import scrape_job, scrape_multiple_jobs
from gmail_module.gmail_api import GmailAPI


def get_job_details_from_email(email_id: str) -> List[Dict[str, Any]]:
    """
    Extract job URLs from a specific email and scrape complete job details.
    
    Args:
        email_id: Gmail message ID
        
    Returns:
        List of complete job data dictionaries with scraped details
    """
    # Extract URLs from email
    gmail = GmailAPI()
    job_urls = gmail.extract_job_urls(email_id)
    
    # Scrape each job URL
    job_details = []
    for url_info in job_urls:
        try:
            job_data = scrape_job(url_info['url'])
            if job_data:
                # Add original email context
                job_data['source_email_id'] = email_id
                job_data['original_link_text'] = url_info.get('link_text', '')
                job_details.append(job_data)
        except Exception as e:
            print(f"Failed to scrape {url_info['url']}: {e}")
    
    return job_details


def scrape_jobs_from_email_urls(email_id: str, urls: List[str]) -> List[Dict[str, Any]]:
    """
    Scrape job details from a list of URLs with email context.
    
    Args:
        email_id: Source Gmail message ID (for context)
        urls: List of LinkedIn job URLs to scrape
        
    Returns:
        List of scraped job data dictionaries
    """
    job_details = []
    
    for url in urls:
        try:
            job_data = scrape_job(url)
            if job_data:
                # Add email context
                job_data['source_email_id'] = email_id
                job_details.append(job_data)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
    
    return job_details


def scrape_jobs_from_url_list(urls: List[str], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Scrape job details from a list of URLs with optional context.
    
    Args:
        urls: List of LinkedIn job URLs to scrape
        context: Optional context dictionary (e.g., source info)
        
    Returns:
        List of scraped job data dictionaries
    """
    job_details = []
    
    for url in urls:
        try:
            job_data = scrape_job(url)
            if job_data:
                # Add context if provided
                if context:
                    job_data['context'] = context
                job_details.append(job_data)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
    
    return job_details


def process_linkedin_emails(email_ids: List[str], max_jobs_per_email: int = 5) -> Dict[str, Any]:
    """
    Process multiple LinkedIn emails and extract all job details.
    
    Args:
        email_ids: List of Gmail message IDs
        max_jobs_per_email: Maximum number of jobs to scrape per email
        
    Returns:
        Dictionary with processed results summary and job details
    """
    gmail = GmailAPI()
    results = {
        'total_emails_processed': 0,
        'total_jobs_found': 0,
        'total_jobs_scraped': 0,
        'emails': {},
        'all_jobs': []
    }
    
    for email_id in email_ids:
        try:
            # Get job URLs from email
            job_urls = gmail.extract_job_urls(email_id)
            results['emails'][email_id] = {
                'job_urls_found': len(job_urls),
                'jobs_scraped': 0,
                'jobs': []
            }
            
            # Limit jobs per email
            urls_to_scrape = job_urls[:max_jobs_per_email]
            
            # Scrape jobs
            for url_info in urls_to_scrape:
                try:
                    job_data = scrape_job(url_info['url'])
                    if job_data:
                        job_data['source_email_id'] = email_id
                        job_data['original_link_text'] = url_info.get('link_text', '')
                        
                        results['emails'][email_id]['jobs'].append(job_data)
                        results['all_jobs'].append(job_data)
                        results['emails'][email_id]['jobs_scraped'] += 1
                        results['total_jobs_scraped'] += 1
                except Exception as e:
                    print(f"Failed to scrape {url_info['url']}: {e}")
            
            results['total_emails_processed'] += 1
            results['total_jobs_found'] += len(job_urls)
            
        except Exception as e:
            print(f"Failed to process email {email_id}: {e}")
    
    return results 