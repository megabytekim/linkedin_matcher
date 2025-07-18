#!/usr/bin/env python3
"""
Extract real LinkedIn job URLs from Gmail for testing.

This script connects to Gmail, finds LinkedIn emails, and extracts job URLs
that can be used for testing the scraper with real data.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from gmail_module.gmail_api import GmailAPI
from config import DEFAULT_QUERY


def extract_job_urls_from_gmail(max_emails: int = 5, max_urls_per_email: int = 3):
    """
    Extract real LinkedIn job URLs from Gmail.
    
    Args:
        max_emails: Maximum number of emails to process
        max_urls_per_email: Maximum URLs to extract per email
        
    Returns:
        List of dictionaries with job URL info
    """
    print("📬 Extracting Real Job URLs from Gmail")
    print("=" * 50)
    
    try:
        # Initialize Gmail API
        print("🔐 Connecting to Gmail...")
        gmail = GmailAPI()
        
        # Get LinkedIn emails
        print(f"🔍 Searching for LinkedIn emails with query: {DEFAULT_QUERY}")
        emails = gmail.list_messages(query=DEFAULT_QUERY, max_results=max_emails)
        
        if not emails:
            print("❌ No LinkedIn emails found. Trying broader search...")
            emails = gmail.list_messages(query="subject:job", max_results=max_emails)
        
        if not emails:
            print("❌ No job-related emails found.")
            return []
        
        print(f"✅ Found {len(emails)} emails to process")
        
        all_job_urls = []
        
        # Extract URLs from each email
        for i, email in enumerate(emails, 1):
            print(f"\n📧 Processing email {i}/{len(emails)}")
            print(f"   Subject: {email['subject'][:70]}...")
            print(f"   From: {email['from']}")
            
            # Extract job URLs
            job_urls = gmail.extract_job_urls(email['id'])
            
            if job_urls:
                # Limit URLs per email to avoid overwhelming
                limited_urls = job_urls[:max_urls_per_email]
                print(f"   ✅ Found {len(job_urls)} URLs, taking first {len(limited_urls)}")
                
                for j, url_info in enumerate(limited_urls, 1):
                    print(f"      {j}. {url_info['url'][:60]}...")
                    
                    # Add email context to URL info
                    url_info['email_subject'] = email['subject']
                    url_info['email_from'] = email['from']
                    url_info['email_id'] = email['id']
                    
                    all_job_urls.append(url_info)
            else:
                print(f"   ❌ No job URLs found in this email")
        
        return all_job_urls
        
    except Exception as e:
        print(f"❌ Error extracting URLs: {e}")
        return []


def save_job_urls(job_urls: list, filename: str = None):
    """Save extracted job URLs to a JSON file."""
    if filename is None:
        # Save to scraper_module/data/ directory
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)
        filename = data_dir / "real_job_urls.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(job_urls, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(job_urls)} job URLs to {filename}")
        return str(filename)
    except Exception as e:
        print(f"❌ Error saving URLs: {e}")
        return None


def create_test_url_list(job_urls: list, max_test_urls: int = 3):
    """Create a smaller list for scraper testing."""
    if not job_urls:
        return []
    
    # Take diverse URLs from different emails if possible
    test_urls = []
    seen_emails = set()
    
    for url_info in job_urls:
        if len(test_urls) >= max_test_urls:
            break
            
        email_id = url_info.get('email_id')
        if email_id not in seen_emails:
            test_urls.append(url_info)
            seen_emails.add(email_id)
    
    # Fill remaining slots if we don't have enough unique emails
    while len(test_urls) < max_test_urls and len(test_urls) < len(job_urls):
        for url_info in job_urls:
            if len(test_urls) >= max_test_urls:
                break
            if url_info not in test_urls:
                test_urls.append(url_info)
    
    return test_urls


def main():
    """Main function to extract and save job URLs."""
    print("🔗 LinkedIn Job URL Extractor")
    print("=" * 60)
    print("🎯 Purpose: Extract real LinkedIn job URLs from Gmail for testing")
    print("⚠️  Note: These URLs will be used for scraper testing with rate limiting")
    print()
    
    # Create data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Extract URLs from Gmail
    job_urls = extract_job_urls_from_gmail(max_emails=10, max_urls_per_email=2)
    
    if not job_urls:
        print("\n❌ No job URLs extracted. Please check:")
        print("  - You have LinkedIn emails in Gmail")
        print("  - Gmail API is properly configured")
        print("  - Your .env file has correct settings")
        return
    
    print(f"\n📊 Extraction Summary:")
    print(f"  Total URLs extracted: {len(job_urls)}")
    
    # Show some examples
    print(f"\n🔗 Sample URLs:")
    for i, url_info in enumerate(job_urls[:3], 1):
        print(f"  {i}. {url_info['url'][:70]}...")
        print(f"     From: {url_info['email_subject'][:50]}...")
    
    # Save all URLs
    all_urls_file = save_job_urls(job_urls, data_dir / "all_job_urls.json")
    
    # Create test subset
    test_urls = create_test_url_list(job_urls, max_test_urls=3)
    test_urls_file = save_job_urls(test_urls, data_dir / "test_job_urls.json")
    
    print(f"\n✅ Job URL extraction completed!")
    print(f"📁 Files created:")
    if all_urls_file:
        print(f"  - {all_urls_file} ({len(job_urls)} URLs)")
    if test_urls_file:
        print(f"  - {test_urls_file} ({len(test_urls)} URLs for testing)")
    
    print(f"\n🧪 Next steps:")
    print(f"  1. Test scraper with: python scraper_module/test_real_scraping.py")
    print(f"  2. Run unit tests: python run_tests.py")
    print(f"  3. Run demo: python demo.py")
    
    print(f"\n⚠️  Rate limiting notes:")
    print(f"  - Scraper includes 2-5 second delays between requests")
    print(f"  - Additional 1-3 second delays for multiple jobs")
    print(f"  - Random timing to avoid detection patterns")


if __name__ == "__main__":
    main() 