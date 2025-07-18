#!/usr/bin/env python3
"""
Test real job scraping with extracted LinkedIn URLs.

This script uses real LinkedIn job URLs extracted from Gmail to test
the scraper functionality with proper rate limiting.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scraper_module.job_scraper import JobScraper


def load_test_urls(filename: str = None):
    """Load test URLs from JSON file."""
    if filename is None:
        # Default to scraper_module/data/test_job_urls.json
        filename = Path(__file__).parent / "data" / "test_job_urls.json"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print("💡 Run 'python scraper_module/extract_real_job_urls.py' first to extract URLs from Gmail")
        return []
    except Exception as e:
        print(f"❌ Error loading URLs: {e}")
        return []


def save_scraping_results(results: list, filename: str = None):
    """Save scraping results to JSON file."""
    if filename is None:
        # Save to scraper_module/data/scraping_results.json
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)
        filename = data_dir / "scraping_results.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved scraping results to {filename}")
        return str(filename)
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        return None


def test_single_job_scraping():
    """Test scraping a single job to verify the scraper works."""
    print("🌐 Testing Single Job Scraping")
    print("=" * 50)
    
    # Load test URLs
    test_urls = load_test_urls()
    
    if not test_urls:
        return False
    
    # Use first URL for single test
    test_url_info = test_urls[0]
    test_url = test_url_info['url']
    
    print(f"📋 Testing with URL from email:")
    print(f"   Subject: {test_url_info.get('email_subject', 'Unknown')[:60]}...")
    print(f"   URL: {test_url[:70]}...")
    print()
    
    # Initialize scraper with conservative rate limiting
    scraper = JobScraper(min_delay=3.0, max_delay=6.0)
    
    print("⚠️  Using conservative rate limiting (3-6 second delays)")
    print("🚀 Starting scrape...")
    
    # Scrape the job
    result = scraper.scrape_job_page(test_url, max_content_length=1000)
    
    if result:
        print("\n✅ Successfully scraped job!")
        print("=" * 40)
        print(f"📝 Title: {result.get('title', 'N/A')}")
        print(f"🏢 Company: {result.get('company', 'N/A')}")
        print(f"📍 Location: {result.get('location', 'N/A')}")
        print(f"🔗 Original URL: {result.get('url', 'N/A')[:60]}...")
        print(f"🌐 Guest URL: {result.get('guest_url', 'N/A')[:60]}...")
        print(f"⏰ Scraped at: {result.get('scraped_at', 'N/A')}")
        
        # Show description preview
        description = result.get('description', '')
        if description:
            print(f"\n📄 Description preview (first 300 chars):")
            print(description[:300] + "..." if len(description) > 300 else description)
        
        # Show job details
        job_details = result.get('jobDetails', [])
        if job_details:
            print(f"\n🏷️  Job details: {', '.join(job_details[:5])}")
        
        return True
    else:
        print("\n❌ Failed to scrape job")
        print("💡 Possible reasons:")
        print("  - LinkedIn blocked the request")
        print("  - Network issues")
        print("  - Job URL is no longer valid")
        print("  - Rate limiting not sufficient")
        return False


def test_multiple_jobs_scraping():
    """Test scraping multiple jobs with enhanced rate limiting."""
    print("\n🌐 Testing Multiple Jobs Scraping")
    print("=" * 50)
    
    # Load test URLs
    test_urls = load_test_urls()
    
    if not test_urls:
        return []
    
    # Limit to 2 jobs for testing to avoid being blocked
    max_jobs = min(2, len(test_urls))
    test_batch = test_urls[:max_jobs]
    
    print(f"📋 Testing with {len(test_batch)} job URLs")
    print("⚠️  Using enhanced rate limiting to avoid being blocked")
    print()
    
    # Extract just the URLs
    urls_to_scrape = [url_info['url'] for url_info in test_batch]
    
    # Initialize scraper with enhanced rate limiting
    scraper = JobScraper(min_delay=4.0, max_delay=8.0)
    
    print("🚀 Starting batch scrape...")
    
    # Scrape multiple jobs
    results = scraper.scrape_multiple_jobs(urls_to_scrape, max_content_length=800)
    
    if results:
        print(f"\n✅ Successfully scraped {len(results)}/{len(test_batch)} jobs!")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\n📋 Job {i}:")
            print(f"   📝 Title: {result.get('title', 'N/A')}")
            print(f"   🏢 Company: {result.get('company', 'N/A')}")
            print(f"   📍 Location: {result.get('location', 'N/A')}")
            
            # Add email context back to results
            original_url = result.get('url', '')
            for url_info in test_batch:
                if url_info['url'] == original_url:
                    result['email_subject'] = url_info.get('email_subject', '')
                    result['email_from'] = url_info.get('email_from', '')
                    print(f"   📧 From email: {result['email_subject'][:50]}...")
                    break
        
        # Save results
        save_scraping_results(results)
        
        return results
    else:
        print("\n❌ No jobs successfully scraped")
        return []


def analyze_scraping_results(results: list):
    """Analyze and summarize scraping results."""
    if not results:
        return
    
    print("\n📊 Scraping Results Analysis")
    print("=" * 50)
    
    # Basic stats
    total_jobs = len(results)
    jobs_with_title = sum(1 for r in results if r.get('title'))
    jobs_with_company = sum(1 for r in results if r.get('company'))
    jobs_with_location = sum(1 for r in results if r.get('location'))
    jobs_with_description = sum(1 for r in results if r.get('description'))
    
    print(f"📈 Success rates:")
    print(f"   Total jobs scraped: {total_jobs}")
    print(f"   Jobs with title: {jobs_with_title}/{total_jobs} ({jobs_with_title/total_jobs*100:.1f}%)")
    print(f"   Jobs with company: {jobs_with_company}/{total_jobs} ({jobs_with_company/total_jobs*100:.1f}%)")
    print(f"   Jobs with location: {jobs_with_location}/{total_jobs} ({jobs_with_location/total_jobs*100:.1f}%)")
    print(f"   Jobs with description: {jobs_with_description}/{total_jobs} ({jobs_with_description/total_jobs*100:.1f}%)")
    
    # Show unique companies
    companies = [r.get('company') for r in results if r.get('company')]
    if companies:
        print(f"\n🏢 Companies found: {', '.join(set(companies))}")
    
    # Show unique locations
    locations = [r.get('location') for r in results if r.get('location')]
    if locations:
        print(f"📍 Locations found: {', '.join(set(locations))}")


def main():
    """Main testing function."""
    print("🧪 Real LinkedIn Job Scraping Test")
    print("=" * 60)
    print("🎯 Purpose: Test job scraping with real URLs and rate limiting")
    print("⚠️  Note: This will make actual requests to LinkedIn")
    print()
    
    # Check if we have test URLs
    test_urls_file = Path(__file__).parent / "data" / "test_job_urls.json"
    if not test_urls_file.exists():
        print("❌ No test URLs found!")
        print("💡 Please run 'python scraper_module/extract_real_job_urls.py' first")
        return
    
    # Test single job scraping first
    single_success = test_single_job_scraping()
    
    if not single_success:
        print("\n⚠️  Single job scraping failed. Stopping here.")
        print("💡 Check your internet connection and try again later")
        return
    
    # If single job works, try multiple jobs
    print("\n" + "=" * 60)
    print("✅ Single job scraping successful! Proceeding to multiple jobs...")
    
    results = test_multiple_jobs_scraping()
    
    # Analyze results
    analyze_scraping_results(results)
    
    print("\n" + "=" * 60)
    print("🎉 Real scraping test completed!")
    
    if results:
        print(f"✅ Successfully tested with {len(results)} real job pages")
        print("🔧 Scraper is working with proper rate limiting")
        print("\n🚀 Ready for:")
        print("  - Unit tests: python run_tests.py")
        print("  - MCP server testing")
        print("  - Production use")
    else:
        print("⚠️  No successful scrapes - may need to adjust rate limiting")
        print("💡 Try again later or increase delays in JobScraper")
    
    print(f"\n📁 Check 'scraper_module/data/' folder for saved results and URLs")


if __name__ == "__main__":
    main() 