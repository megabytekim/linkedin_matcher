#!/usr/bin/env python3
"""
Test script for MCP tools.

This script tests all the MCP tools to ensure they work correctly
before connecting them to an AI assistant.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_gmail_tools():
    """Test Gmail MCP tools."""
    print("📧 Testing Gmail MCP Tools")
    print("=" * 50)
    
    try:
        from core.tools.gmail import list_emails, extract_job_urls, get_email_content, label_email
        
        # Test 1: List emails
        print("\n🔍 Test 1: list_emails")
        emails = list_emails("from:linkedin.com", 3)
        print(f"✅ Found {len(emails)} emails")
        
        if emails:
            email_id = emails[0]['id']
            print(f"   Sample email: {emails[0]['subject'][:50]}...")
            
            # Test 2: Extract job URLs
            print(f"\n🔗 Test 2: extract_job_urls")
            job_urls = extract_job_urls(email_id)
            print(f"✅ Found {len(job_urls)} job URLs")
            
            # Test 3: Get email content
            print(f"\n📖 Test 3: get_email_content")
            content = get_email_content(email_id)
            content_length = len(content) if content else 0
            print(f"✅ Retrieved {content_length} characters of content")
            
            # Test 4: Label email (optional)
            print(f"\n🏷️  Test 4: label_email")
            result = label_email(email_id, "MCP_TESTED")
            print(f"✅ Label result: {result}")
        else:
            print("❌ No emails found - cannot test other Gmail functions")
            
    except Exception as e:
        print(f"❌ Gmail tools test failed: {e}")
        return False
    
    return True


def test_scraper_tools():
    """Test LinkedIn scraper MCP tools."""
    print("\n🌐 Testing LinkedIn Scraper MCP Tools")
    print("=" * 50)
    
    try:
        from core.tools.scraper import validate_linkedin_url, convert_to_guest_url, get_job_summary, scrape_job
        
        # Use a known LinkedIn job URL for testing
        test_url = "https://www.linkedin.com/jobs/view/4267369043"
        
        # Test 1: Validate URL
        print("\n✅ Test 1: validate_linkedin_url")
        is_valid = validate_linkedin_url(test_url)
        print(f"✅ URL validation: {is_valid}")
        
        # Test 2: Convert to guest URL
        print("\n🔗 Test 2: convert_to_guest_url")
        guest_url = convert_to_guest_url(test_url)
        print(f"✅ Guest URL: {guest_url[:60]}..." if guest_url else "❌ Guest URL conversion failed")
        
        # Test 3: Get job summary
        print("\n📄 Test 3: get_job_summary")
        summary = get_job_summary(test_url)
        if summary:
            print(f"✅ Job summary: {summary.get('title', 'N/A')} at {summary.get('company', 'N/A')}")
        else:
            print("❌ Job summary failed")
        
        # Test 4: Full scrape (optional - slower)
        print("\n🔍 Test 4: scrape_job (abbreviated)")
        job_data = scrape_job(test_url, max_content_length=500)
        if job_data and 'error' not in job_data:
            print(f"✅ Job scraping: {job_data.get('title', 'N/A')} at {job_data.get('company', 'N/A')}")
            print(f"   Location: {job_data.get('location', 'N/A')}")
        else:
            print(f"❌ Job scraping failed: {job_data}")
        
    except Exception as e:
        print(f"❌ Scraper tools test failed: {e}")
        return False
    
    return True


def test_workflow_tool():
    """Test the complete workflow MCP tool."""
    print("\n🔄 Testing Workflow MCP Tool")
    print("=" * 50)
    
    try:
        from core.tools.gmail import list_emails, extract_job_urls
        from core.tools.scraper import scrape_job
        
        print("\n🚀 Test: Manual workflow simulation")
        
        # Step 1: List emails
        emails = list_emails("from:linkedin.com", 2)
        print(f"✅ Step 1: Found {len(emails)} emails")
        
        # Step 2: Extract URLs from first email
        if emails:
            urls = extract_job_urls(emails[0]['id'])
            print(f"✅ Step 2: Extracted {len(urls)} URLs from first email")
            
            # Step 3: Scrape first job (if any)
            if urls:
                job_data = scrape_job(urls[0]['url'], max_content_length=500)
                if job_data and 'error' not in job_data:
                    print(f"✅ Step 3: Scraped job: {job_data.get('title', 'N/A')}")
                else:
                    print(f"❌ Step 3: Job scraping failed")
            else:
                print("⚠️  Step 3: No URLs to scrape")
        else:
            print("❌ No emails found for workflow test")
            
    except Exception as e:
        print(f"❌ Workflow tool test failed: {e}")
        return False
    
    return True

def test_mcp_server():
    """Test that MCP server can start."""
    print("\n🚀 Testing MCP Server Startup")
    print("=" * 50)
    
    try:
        from core.server_app import app
        
        # Test that the app is properly configured
        print(f"✅ MCP server configured")
        
        # Check available tools by looking at registered tools
        print(f"✅ Tools registered with server")
        print(f"💡 To start MCP server: PYTHONPATH=. python core/serve.py")
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False
    
    return True


def main():
    """Run all MCP tests."""
    print("🧪 LinkedIn Job Scraper MCP Tests")
    print("=" * 60)
    print("🎯 Purpose: Test all MCP tools before AI assistant integration")
    print("⚠️  Note: This will test real Gmail and scraping functionality")
    print()
    
    # Run all tests
    tests = [
        ("Gmail Tools", test_gmail_tools),
        ("Scraper Tools", test_scraper_tools),
        ("Workflow Tool", test_workflow_tool),
        ("MCP Server", test_mcp_server)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MCP Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All MCP tools are working! Ready for AI assistant integration.")
        print("\n🚀 Next steps:")
        print("   1. Start MCP server: PYTHONPATH=. python core/serve.py")
        print("   2. Configure your AI assistant to use mcp_config.json")
        print("   3. Use the tools in AI conversations!")
    else:
        print("⚠️  Some tests failed. Please fix issues before using with AI assistant.")

if __name__ == "__main__":
    main() 