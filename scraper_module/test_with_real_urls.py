#!/usr/bin/env python3
"""
Test scraper with real LinkedIn job URLs from visible folder.

This script loads real URLs that were extracted from Gmail and saved
to the visible_urls folder, then tests the scraper with them.
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scraper_module.job_scraper import JobScraper


def load_real_urls_from_visible_folder(filename: str = None):
    """Load real URLs from the visible_urls folder."""
    if filename is None:
        # Default to test_real_urls.json
        filename = Path(__file__).parent / "visible_urls" / "test_real_urls.json"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract URLs from the data
        if isinstance(data, list):
            urls = []
            for item in data:
                if isinstance(item, dict) and 'url' in item:
                    urls.append(item['url'])
                elif isinstance(item, str):
                    urls.append(item)
            return urls
        elif isinstance(data, dict) and 'urls' in data:
            return data['urls']
        else:
            print(f"❌ Unexpected data format in {filename}")
            return []
            
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {filename}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error loading URLs from {filename}: {e}")
        return []


async def test_single_real_job():
    """Test scraping a single real job URL."""
    print("🌐 Testing Single Real Job Scraping")
    print("=" * 50)
    
    # Load real URLs
    urls = load_real_urls_from_visible_folder()
    if not urls:
        print("❌ No real URLs found for testing")
        return None
    
    # Use the first URL for single job test
    test_url = urls[0]
    
    # Load the full data to show context
    data_file = Path(__file__).parent / "visible_urls" / "test_real_urls.json"
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        if isinstance(full_data, list) and len(full_data) > 0:
            job_info = full_data[0]
            print(f"📋 Testing with REAL URL from Gmail:")
            print(f"   Subject: {job_info.get('email_subject', 'N/A')[:80]}...")
            print(f"   URL: {job_info.get('url', 'N/A')[:80]}...")
            print(f"   Email Date: {job_info.get('email_date', 'N/A')}")
    except Exception as e:
        print(f"⚠️  Could not load full job info: {e}")
        print(f"📋 Testing with URL: {test_url[:80]}...")
    
    print()
    print("⚠️  Using conservative rate limiting (3-6 second delays)")
    print("🚀 Starting real scrape...")
    print()
    
    # Test with async scraper
    async with JobScraper(min_delay=1.0, max_delay=2.0) as scraper:
        result = await scraper.scrape_job_page(test_url, max_content_length=10000)
    
    if result:
        print()
        print("✅ Successfully scraped real job!")
        print("=" * 40)
        print(f"📝 Title: {result.get('title', 'N/A')}")
        print(f"🏢 Company: {result.get('company', 'N/A')}")
        print(f"📍 Location: {result.get('location', 'N/A')}")
        print(f"📄 Page Title: {result.get('pageTitle', 'N/A')[:100]}...")
        print(f"📝 Description Length: {len(result.get('description', ''))} characters")
        print(f"🔗 Guest URL: {result.get('guest_url', 'N/A')}")
        print(f"⏰ Scraped At: {result.get('scraped_at', 'N/A')}")
        
        # Show job details
        job_details = result.get('jobDetails', [])
        if job_details:
            print(f"🏷️  Job Details ({len(job_details)} items):")
            for i in range(0, len(job_details), 2):
                if i + 1 < len(job_details):
                    print(f"   • {job_details[i]}: {job_details[i+1]}")
                else:
                    print(f"   • {job_details[i]}")
        
        # Show description preview
        description = result.get('description', '')
        if description:
            print(f"\n📝 Description Preview:")
            print("-" * 40)
            print(description[:500] + "..." if len(description) > 500 else description)
            print("-" * 40)
        
        return result
    else:
        print("❌ Failed to scrape real job")
        return None


async def test_multiple_real_jobs():
    """Test scraping multiple real job URLs."""
    print("\n🌐 Testing Multiple Real Jobs Scraping")
    print("=" * 50)
    
    # Load real URLs
    urls = load_real_urls_from_visible_folder()
    if not urls:
        print("❌ No real URLs found for testing")
        return []
    
    # Limit to first 3 URLs for testing
    test_urls = urls[:3]
    print(f"📋 Testing with {len(test_urls)} real URLs from Gmail")
    print("⚠️  Using conservative rate limiting (3-6 second delays)")
    print("🚀 Starting batch scrape...")
    print()
    
    # Test with async scraper
    async with JobScraper(min_delay=1.0, max_delay=2.0) as scraper:
        results = await scraper.scrape_multiple_jobs(test_urls, max_content_length=10000)
    
    if results:
        print(f"\n✅ Successfully scraped {len(results)} real jobs!")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\n📋 Job {i}:")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Company: {result.get('company', 'N/A')}")
            print(f"   Location: {result.get('location', 'N/A')}")
            print(f"   Description Length: {len(result.get('description', ''))} characters")
            print(f"   Guest URL: {result.get('guest_url', 'N/A')}")
        
        # Save results for inspection
        results_file = Path(__file__).parent / "visible_urls" / "real_scraping_results.json"
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {results_file}")
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")
        
        return results
    else:
        print("❌ Failed to scrape any real jobs")
        return []


def compare_with_previous_results():
    """Compare new results with previous scraping results."""
    print("\n📊 Comparing with Previous Results")
    print("=" * 50)
    
    # Load previous results
    previous_file = Path(__file__).parent / "visible_urls" / "real_scraping_results.json"
    if not previous_file.exists():
        print("ℹ️  No previous results found for comparison")
        return
    
    try:
        with open(previous_file, 'r', encoding='utf-8') as f:
            previous_results = json.load(f)
        
        print(f"📈 Previous scraping results:")
        print(f"   Total jobs: {len(previous_results)}")
        
        for i, job in enumerate(previous_results, 1):
            print(f"   Job {i}: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            print(f"      Description length: {len(job.get('description', ''))} characters")
        
        # Analyze description completeness
        descriptions = [job.get('description', '') for job in previous_results]
        avg_length = sum(len(d) for d in descriptions) / len(descriptions) if descriptions else 0
        max_length = max(len(d) for d in descriptions) if descriptions else 0
        min_length = min(len(d) for d in descriptions) if descriptions else 0
        
        print(f"\n📝 Description Analysis:")
        print(f"   Average length: {avg_length:.0f} characters")
        print(f"   Maximum length: {max_length} characters")
        print(f"   Minimum length: {min_length} characters")
        
        # Check for truncated descriptions
        truncated_count = sum(1 for d in descriptions if len(d) < 500)
        print(f"   Likely truncated: {truncated_count}/{len(descriptions)}")
        
    except Exception as e:
        print(f"❌ Error loading previous results: {e}")


async def main():
    """Main test function."""
    print("🧪 Real LinkedIn Job Scraping Test")
    print("=" * 60)
    print("🎯 Purpose: Test scraper with REAL URLs from your Gmail")
    print("📁 Source: scraper_module/visible_urls/")
    print("⚠️  Note: This will make actual requests to LinkedIn")
    print()
    
    # Test single job scraping
    single_result = await test_single_real_job()
    
    # Test multiple job scraping
    multiple_results = await test_multiple_real_jobs()
    
    # Compare with previous results
    compare_with_previous_results()
    
    print("\n🎉 Real URL Testing Complete!")
    print("=" * 60)
    
    if single_result:
        print("✅ Single job scraping: SUCCESS")
    else:
        print("❌ Single job scraping: FAILED")
    
    if multiple_results:
        print(f"✅ Multiple job scraping: SUCCESS ({len(multiple_results)} jobs)")
    else:
        print("❌ Multiple job scraping: FAILED")
    
    print("\n💡 Next steps:")
    print("   • Check scraper_module/visible_urls/real_scraping_results.json")
    print("   • Run 'python scraper_module/show_full_results.py' to see complete data")
    print("   • The scraper now handles 'Show more' button for full descriptions!")


if __name__ == "__main__":
    asyncio.run(main()) 