#!/usr/bin/env python3
"""
Save sample LinkedIn job URLs for manual testing and inspection.

This script creates sample URLs that you can see with your own eyes
and use for testing the scraper module.
"""

import json
import os
from pathlib import Path


def create_sample_urls():
    """Create sample LinkedIn job URLs for testing."""
    
    # Sample URLs that look like real LinkedIn job URLs
    sample_urls = [
        {
            "url": "https://www.linkedin.com/jobs/view/1234567890/",
            "title": "Sample Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA",
            "description": "Sample job description for testing purposes",
            "email_subject": "Sample LinkedIn Job Alert",
            "email_from": "LinkedIn Jobs <jobs-noreply@linkedin.com>",
            "email_id": "sample_email_1"
        },
        {
            "url": "https://www.linkedin.com/comm/jobs/view/9876543210/",
            "title": "Sample Data Scientist",
            "company": "AI Startup",
            "location": "New York, NY",
            "description": "Another sample job for testing the scraper",
            "email_subject": "Data Science Opportunities",
            "email_from": "LinkedIn Jobs <jobs-noreply@linkedin.com>",
            "email_id": "sample_email_2"
        },
        {
            "url": "https://www.linkedin.com/jobs/view/5556667778/",
            "title": "Sample Product Manager",
            "company": "Big Tech Inc",
            "location": "Seattle, WA",
            "description": "Product management role for testing",
            "email_subject": "Product Management Jobs",
            "email_from": "LinkedIn Jobs <jobs-noreply@linkedin.com>",
            "email_id": "sample_email_3"
        },
        {
            "url": "https://www.linkedin.com/comm/jobs/view/1112223334/",
            "title": "Sample DevOps Engineer",
            "company": "Cloud Company",
            "location": "Austin, TX",
            "description": "DevOps engineering position for testing",
            "email_subject": "DevOps Engineering Roles",
            "email_from": "LinkedIn Jobs <jobs-noreply@linkedin.com>",
            "email_id": "sample_email_4"
        },
        {
            "url": "https://www.linkedin.com/jobs/view/9998887776/",
            "title": "Sample UX Designer",
            "company": "Design Studio",
            "location": "Los Angeles, CA",
            "description": "UX design role for testing the scraper",
            "email_subject": "Design Opportunities",
            "email_from": "LinkedIn Jobs <jobs-noreply@linkedin.com>",
            "email_id": "sample_email_5"
        }
    ]
    
    return sample_urls


def save_urls_to_visible_location():
    """Save URLs to a visible subfolder for manual inspection."""
    
    # Create a visible subfolder
    visible_folder = Path(__file__).parent / "visible_urls"
    visible_folder.mkdir(exist_ok=True)
    
    # Get sample URLs
    sample_urls = create_sample_urls()
    
    # Save all URLs
    all_urls_file = visible_folder / "all_sample_urls.json"
    with open(all_urls_file, 'w', encoding='utf-8') as f:
        json.dump(sample_urls, f, indent=2, ensure_ascii=False)
    
    # Save a smaller subset for quick testing
    test_urls = sample_urls[:3]
    test_urls_file = visible_folder / "test_sample_urls.json"
    with open(test_urls_file, 'w', encoding='utf-8') as f:
        json.dump(test_urls, f, indent=2, ensure_ascii=False)
    
    # Save just the URLs as a simple text file
    urls_only_file = visible_folder / "urls_only.txt"
    with open(urls_only_file, 'w', encoding='utf-8') as f:
        for url_info in sample_urls:
            f.write(f"{url_info['url']}\n")
    
    # Save a human-readable summary
    summary_file = visible_folder / "url_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("LinkedIn Job URLs for Testing\n")
        f.write("=" * 40 + "\n\n")
        
        for i, url_info in enumerate(sample_urls, 1):
            f.write(f"URL {i}:\n")
            f.write(f"  Job: {url_info['title']}\n")
            f.write(f"  Company: {url_info['company']}\n")
            f.write(f"  Location: {url_info['location']}\n")
            f.write(f"  URL: {url_info['url']}\n")
            f.write(f"  From Email: {url_info['email_subject']}\n")
            f.write("\n")
    
    return {
        "folder": str(visible_folder),
        "all_urls": str(all_urls_file),
        "test_urls": str(test_urls_file),
        "urls_only": str(urls_only_file),
        "summary": str(summary_file),
        "count": len(sample_urls)
    }


def main():
    """Main function to save URLs for manual inspection."""
    print("🔗 Saving Sample LinkedIn Job URLs")
    print("=" * 50)
    print("🎯 Purpose: Create sample URLs you can see with your own eyes")
    print("📁 Location: scraper_module/visible_urls/")
    print()
    
    # Save URLs
    result = save_urls_to_visible_location()
    
    print("✅ URLs saved successfully!")
    print(f"📁 Folder: {result['folder']}")
    print(f"📊 Total URLs: {result['count']}")
    print()
    
    print("📄 Files created:")
    print(f"  📋 {result['all_urls']} - All URLs with full details")
    print(f"  🧪 {result['test_urls']} - Test subset (3 URLs)")
    print(f"  🔗 {result['urls_only']} - Just the URLs (one per line)")
    print(f"  📝 {result['summary']} - Human-readable summary")
    print()
    
    print("👀 You can now:")
    print("  1. Open the folder and look at the files")
    print("  2. Use these URLs for testing the scraper")
    print("  3. Modify the URLs in the JSON files")
    print("  4. Add your own real LinkedIn job URLs")
    print()
    
    print("🧪 To test with these URLs:")
    print("  python scraper_module/test_with_sample_urls.py")
    print()
    
    print("💡 Note: These are sample URLs - they won't work for real scraping")
    print("   For real testing, use URLs from: python scraper_module/extract_real_job_urls.py")


if __name__ == "__main__":
    main() 