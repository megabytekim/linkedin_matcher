#!/usr/bin/env python3
"""Test script for job URL extraction and scraping functionality."""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gmail_module.gmail_api import GmailAPI
from config import DEFAULT_QUERY


def test_url_extraction():
    """Test extracting job URLs from LinkedIn emails."""
    print("🔗 Testing Job URL Extraction...")
    print("=" * 50)
    
    try:
        # Initialize Gmail API
        gmail = GmailAPI()
        
        # Get LinkedIn emails
        print("\n🔍 Step 1: Finding LinkedIn emails...")
        emails = gmail.list_messages(query=DEFAULT_QUERY, max_results=3)
        
        if not emails:
            print("No LinkedIn emails found. Cannot test URL extraction.")
            return []
        
        all_job_urls = []
        
        # Extract URLs from each email
        for i, email in enumerate(emails, 1):
            print(f"\n📧 Test {i}: Extracting URLs from email")
            print("-" * 40)
            print(f"Subject: {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Email ID: {email['id']}")
            
            # Extract job URLs
            job_urls = gmail.extract_job_urls(email['id'])
            
            if job_urls:
                print(f"✅ Found {len(job_urls)} job URLs:")
                for j, job_url in enumerate(job_urls, 1):
                    print(f"  {j}. {job_url['url']}")
                    print(f"     Link text: '{job_url['link_text']}'")
                    print()
                
                all_job_urls.extend(job_urls)
            else:
                print("❌ No job URLs found in this email")
            
            print("-" * 50)
        
        return all_job_urls
        
    except Exception as e:
        print(f"❌ Error during URL extraction test: {e}")
        return []


def test_job_scraping(job_urls):
    """Test scraping job pages with Playwright."""
    print("\n🌐 Testing Job Page Scraping...")
    print("=" * 50)
    
    if not job_urls:
        print("No job URLs to scrape")
        return
    
    try:
        gmail = GmailAPI()
        
        # Test scraping first few job URLs
        test_urls = job_urls[:2]  # Limit to 2 for testing
        
        for i, job_url_info in enumerate(test_urls, 1):
            url = job_url_info['url']
            print(f"\n🔍 Test {i}: Scraping job page")
            print("-" * 40)
            print(f"URL: {url}")
            print(f"Link text: '{job_url_info['link_text']}'")
            
            # Scrape job page
            job_data = gmail.scrape_job_page(url, max_content_length=500)
            
            if job_data:
                print("✅ Successfully scraped job data:")
                print(f"  Title: {job_data.get('title', 'N/A')}")
                print(f"  Company: {job_data.get('company', 'N/A')}")
                print(f"  Location: {job_data.get('location', 'N/A')}")
                print(f"  Description: {job_data.get('description', 'N/A')[:200]}...")
                print(f"  Scraped at: {job_data.get('scraped_at', 'N/A')}")
            else:
                print("❌ Failed to scrape job data")
            
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error during job scraping test: {e}")


def test_full_workflow():
    """Test the complete workflow: email -> URLs -> job data."""
    print("\n🔄 Testing Complete Workflow...")
    print("=" * 50)
    
    try:
        gmail = GmailAPI()
        
        # Get LinkedIn emails
        emails = gmail.list_messages(query=DEFAULT_QUERY, max_results=2)
        
        if not emails:
            print("No LinkedIn emails found for complete workflow test")
            return
        
        # Test complete workflow for first email
        email = emails[0]
        print(f"\n📧 Processing email: {email['subject']}")
        print("-" * 40)
        
        # Get complete job details from email
        job_details = gmail.get_job_details_from_email(email['id'])
        
        if job_details:
            print(f"✅ Successfully processed {len(job_details)} jobs:")
            
            for i, job in enumerate(job_details, 1):
                print(f"\n  Job {i}:")
                print(f"    Title: {job.get('title', 'N/A')}")
                print(f"    Company: {job.get('company', 'N/A')}")
                print(f"    Location: {job.get('location', 'N/A')}")
                print(f"    URL: {job.get('url', 'N/A')}")
                print(f"    Link text: '{job.get('link_text', 'N/A')}'")
                
                # Save job data to file for inspection
                filename = f"job_data_{i}.json"
                with open(filename, 'w') as f:
                    json.dump(job, f, indent=2)
                print(f"    Saved to: {filename}")
        else:
            print("❌ No job details extracted")
        
    except Exception as e:
        print(f"❌ Error during complete workflow test: {e}")


def main():
    """Run all job scraping tests."""
    print("🧪 LinkedIn Job Scraping Tests")
    print("=" * 60)
    
    # Test 1: URL extraction
    job_urls = test_url_extraction()
    
    # Test 2: Job page scraping (if we have URLs)
    if job_urls:
        test_job_scraping(job_urls)
    
    # Test 3: Complete workflow
    test_full_workflow()
    
    print("\n🎉 Job scraping tests completed!")
    print("\n💡 Note: Make sure you have:")
    print("- Playwright browsers installed (run: playwright install)")
    print("- LinkedIn emails in your Gmail account")
    print("- Stable internet connection for scraping")


if __name__ == "__main__":
    main() 