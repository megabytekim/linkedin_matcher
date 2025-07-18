#!/usr/bin/env python3
"""
Extract real LinkedIn job URLs from Gmail and save to visible folder.

This script uses the Gmail API to find real LinkedIn emails, extract job URLs,
and save them to a visible folder so you can see them with your own eyes.
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


def extract_real_urls_from_gmail(max_emails: int = 10, max_urls_per_email: int = 3):
    """
    Extract real LinkedIn job URLs from Gmail using the Gmail API.
    
    Args:
        max_emails: Maximum number of emails to process
        max_urls_per_email: Maximum URLs to extract per email
        
    Returns:
        List of dictionaries with real job URL info
    """
    print("📬 Extracting Real LinkedIn Job URLs from Gmail")
    print("=" * 60)
    
    try:
        # Initialize Gmail API
        print("🔐 Connecting to Gmail API...")
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
            print(f"   Date: {email.get('date', 'Unknown')}")
            
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
                    url_info['email_date'] = email.get('date', 'Unknown')
                    
                    all_job_urls.append(url_info)
            else:
                print(f"   ❌ No job URLs found in this email")
        
        return all_job_urls
        
    except Exception as e:
        print(f"❌ Error extracting URLs: {e}")
        return []


def save_urls_to_visible_folder(job_urls: list):
    """Save extracted job URLs to a visible folder for manual inspection."""
    
    # Create visible folder
    visible_folder = Path(__file__).parent / "visible_urls"
    visible_folder.mkdir(exist_ok=True)
    
    if not job_urls:
        print("❌ No URLs to save")
        return None
    
    # Save all URLs with full details
    all_urls_file = visible_folder / "real_job_urls.json"
    with open(all_urls_file, 'w', encoding='utf-8') as f:
        json.dump(job_urls, f, indent=2, ensure_ascii=False)
    
    # Save a test subset (first 3 URLs)
    test_urls = job_urls[:3]
    test_urls_file = visible_folder / "test_real_urls.json"
    with open(test_urls_file, 'w', encoding='utf-8') as f:
        json.dump(test_urls, f, indent=2, ensure_ascii=False)
    
    # Save just the URLs as a simple text file
    urls_only_file = visible_folder / "real_urls_only.txt"
    with open(urls_only_file, 'w', encoding='utf-8') as f:
        for url_info in job_urls:
            f.write(f"{url_info['url']}\n")
    
    # Save a human-readable summary
    summary_file = visible_folder / "real_urls_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("Real LinkedIn Job URLs from Gmail\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total URLs extracted: {len(job_urls)}\n")
        f.write(f"Source: Gmail API using query: {DEFAULT_QUERY}\n\n")
        
        for i, url_info in enumerate(job_urls, 1):
            f.write(f"URL {i}:\n")
            f.write(f"  Job: {url_info.get('title', 'N/A')}\n")
            f.write(f"  Company: {url_info.get('company', 'N/A')}\n")
            f.write(f"  Location: {url_info.get('location', 'N/A')}\n")
            f.write(f"  URL: {url_info['url']}\n")
            f.write(f"  From Email: {url_info['email_subject'][:60]}...\n")
            f.write(f"  Email Date: {url_info.get('email_date', 'Unknown')}\n")
            f.write("\n")
    
    # Save email details separately
    email_details_file = visible_folder / "email_details.json"
    email_details = []
    for url_info in job_urls:
        email_detail = {
            "email_id": url_info['email_id'],
            "subject": url_info['email_subject'],
            "from": url_info['email_from'],
            "date": url_info.get('email_date', 'Unknown'),
            "urls_found": len([u for u in job_urls if u['email_id'] == url_info['email_id']])
        }
        if email_detail not in email_details:
            email_details.append(email_detail)
    
    with open(email_details_file, 'w', encoding='utf-8') as f:
        json.dump(email_details, f, indent=2, ensure_ascii=False)
    
    return {
        "folder": str(visible_folder),
        "all_urls": str(all_urls_file),
        "test_urls": str(test_urls_file),
        "urls_only": str(urls_only_file),
        "summary": str(summary_file),
        "email_details": str(email_details_file),
        "count": len(job_urls)
    }


def main():
    """Main function to extract and save real URLs from Gmail."""
    print("🔗 Real LinkedIn Job URL Extractor")
    print("=" * 60)
    print("🎯 Purpose: Extract real LinkedIn job URLs from your Gmail")
    print("📁 Save to: scraper_module/visible_urls/")
    print("⚠️  Note: These are REAL URLs from your actual emails")
    print()
    
    # Extract real URLs from Gmail
    job_urls = extract_real_urls_from_gmail(max_emails=15, max_urls_per_email=2)
    
    if not job_urls:
        print("\n❌ No job URLs extracted. Please check:")
        print("  - You have LinkedIn emails in Gmail")
        print("  - Gmail API is properly configured")
        print("  - Your .env file has correct settings")
        print("  - Try running: python scraper_module/extract_real_job_urls.py")
        return
    
    print(f"\n📊 Extraction Summary:")
    print(f"  Total URLs extracted: {len(job_urls)}")
    
    # Show some examples
    print(f"\n🔗 Sample Real URLs:")
    for i, url_info in enumerate(job_urls[:3], 1):
        print(f"  {i}. {url_info['url'][:70]}...")
        print(f"     From: {url_info['email_subject'][:50]}...")
    
    # Save to visible folder
    result = save_urls_to_visible_folder(job_urls)
    
    print(f"\n✅ Real URLs saved successfully!")
    print(f"📁 Folder: {result['folder']}")
    print(f"📊 Total URLs: {result['count']}")
    print()
    
    print("📄 Files created:")
    print(f"  📋 {result['all_urls']} - All real URLs with full details")
    print(f"  🧪 {result['test_urls']} - Test subset (3 URLs)")
    print(f"  🔗 {result['urls_only']} - Just the URLs (one per line)")
    print(f"  📝 {result['summary']} - Human-readable summary")
    print(f"  📧 {result['email_details']} - Email details")
    print()
    
    print("👀 You can now:")
    print("  1. Open the folder and look at the real URLs")
    print("  2. Use these URLs for real scraping tests")
    print("  3. See which emails contained job URLs")
    print("  4. Test the scraper with actual LinkedIn job pages")
    print()
    
    print("🧪 To test scraping with these real URLs:")
    print("  python scraper_module/test_real_scraping.py")
    print()
    
    print("💡 Next steps:")
    print("  1. Check the files in scraper_module/visible_urls/")
    print("  2. Run real scraping test with the extracted URLs")
    print("  3. Verify the scraper works with actual LinkedIn pages")


if __name__ == "__main__":
    main() 