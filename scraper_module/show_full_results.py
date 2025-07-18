#!/usr/bin/env python3
"""
Display full scraping results in a readable format.

This script shows all the information that was extracted from LinkedIn job pages,
including the complete data that might not be immediately visible.
"""

import json
from pathlib import Path


def display_full_results():
    """Display the complete scraping results."""
    
    # Load the scraping results
    results_file = Path(__file__).parent / "visible_urls" / "real_scraping_results.json"
    
    if not results_file.exists():
        print("❌ No scraping results found!")
        print("💡 Run 'python scraper_module/test_with_real_urls.py' first")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("🔍 FULL SCRAPING RESULTS ANALYSIS")
    print("=" * 80)
    print(f"📊 Total jobs scraped: {len(results)}")
    print()
    
    for i, job in enumerate(results, 1):
        print(f"📋 JOB {i}: {job.get('title', 'N/A')}")
        print("=" * 80)
        
        # Basic info
        print(f"🏢 Company: {job.get('company', 'N/A')}")
        print(f"📍 Location: {job.get('location', 'N/A')}")
        print(f"🔗 Original URL: {job.get('url', 'N/A')[:80]}...")
        print(f"🌐 Guest URL: {job.get('guest_url', 'N/A')}")
        print(f"⏰ Scraped at: {job.get('scraped_at', 'N/A')}")
        print()
        
        # Page title (often contains full location)
        page_title = job.get('pageTitle', '')
        if page_title:
            print(f"📄 Page Title: {page_title}")
            print()
        
        # Job details
        job_details = job.get('jobDetails', [])
        if job_details:
            print("🏷️  Job Details:")
            for j in range(0, len(job_details), 2):
                if j + 1 < len(job_details):
                    print(f"   • {job_details[j]}: {job_details[j+1]}")
                else:
                    print(f"   • {job_details[j]}")
            print()
        
        # Full description
        description = job.get('description', '')
        if description:
            print(f"📝 Full Description ({len(description)} characters):")
            print("-" * 40)
            print(description)
            print("-" * 40)
            print()
        
        # Email context
        print("📧 Email Context:")
        print(f"   Subject: {job.get('email_subject', 'N/A')}")
        print(f"   From: {job.get('email_from', 'N/A')}")
        print(f"   Date: {job.get('email_date', 'N/A')}")
        print()
        
        print("=" * 80)
        print()


def analyze_data_completeness():
    """Analyze how complete the scraped data is."""
    
    results_file = Path(__file__).parent / "visible_urls" / "real_scraping_results.json"
    
    if not results_file.exists():
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("📊 DATA COMPLETENESS ANALYSIS")
    print("=" * 50)
    
    total_jobs = len(results)
    
    # Check each field
    fields = {
        'title': 'Job Title',
        'company': 'Company',
        'location': 'Location',
        'description': 'Description',
        'pageTitle': 'Page Title',
        'jobDetails': 'Job Details',
        'url': 'Original URL',
        'guest_url': 'Guest URL',
        'scraped_at': 'Scraped At',
        'email_subject': 'Email Subject',
        'email_from': 'Email From',
        'email_date': 'Email Date'
    }
    
    for field, label in fields.items():
        present = sum(1 for job in results if job.get(field))
        percentage = (present / total_jobs) * 100
        print(f"{label:15} {present}/{total_jobs} ({percentage:.1f}%)")
    
    print()
    
    # Check description lengths
    descriptions = [job.get('description', '') for job in results]
    if descriptions:
        avg_length = sum(len(d) for d in descriptions) / len(descriptions)
        max_length = max(len(d) for d in descriptions)
        min_length = min(len(d) for d in descriptions)
        
        print("📝 Description Length Analysis:")
        print(f"   Average: {avg_length:.0f} characters")
        print(f"   Maximum: {max_length} characters")
        print(f"   Minimum: {min_length} characters")
        print()
        
        # Show if descriptions are truncated
        for i, desc in enumerate(descriptions, 1):
            if len(desc) < 500:  # Likely truncated
                print(f"   Job {i}: {len(desc)} chars - likely truncated")
            else:
                print(f"   Job {i}: {len(desc)} chars - appears complete")


def main():
    """Main function to display full results."""
    print("🔍 LinkedIn Job Scraping - Full Results Display")
    print("=" * 80)
    print("🎯 Purpose: Show ALL information extracted from LinkedIn job pages")
    print("📁 Source: scraper_module/visible_urls/real_scraping_results.json")
    print()
    
    # Display full results
    display_full_results()
    
    # Analyze data completeness
    analyze_data_completeness()
    
    print("\n💡 Notes:")
    print("  • Descriptions may be truncated due to LinkedIn's guest page limitations")
    print("  • Location field shows company name instead of city/country")
    print("  • Full location info is available in the pageTitle field")
    print("  • All email context and job details are complete")
    print("  • Guest URLs allow scraping without LinkedIn login")


if __name__ == "__main__":
    main() 