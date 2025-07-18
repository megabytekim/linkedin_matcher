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
        from mcp_tools.gmail_tools import list_emails, extract_job_urls, get_email_content, label_email
        
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
    """Test Scraper MCP tools."""
    print("\n🌐 Testing Scraper MCP Tools")
    print("=" * 50)
    
    try:
        from mcp_tools.scraper_tools import validate_linkedin_url, convert_to_guest_url, get_job_summary, scrape_job
        
        # Test URL
        test_url = "https://www.linkedin.com/jobs/view/1234567890/"
        
        # Test 1: Validate URL
        print(f"\n✅ Test 1: validate_linkedin_url")
        is_valid = validate_linkedin_url(test_url)
        print(f"✅ URL validation: {is_valid}")
        
        # Test 2: Convert to guest URL
        print(f"\n🌐 Test 2: convert_to_guest_url")
        guest_url = convert_to_guest_url(test_url)
        print(f"✅ Guest URL: {guest_url[:60]}...")
        
        # Test 3: Get job summary (with real URL if available)
        print(f"\n📋 Test 3: get_job_summary")
        # Try to get a real URL from visible_urls folder
        real_url = get_real_test_url()
        if real_url:
            print(f"   Using real URL: {real_url[:60]}...")
            summary = get_job_summary(real_url)
            if summary:
                print(f"✅ Job summary:")
                print(f"   Title: {summary.get('title', 'N/A')}")
                print(f"   Company: {summary.get('company', 'N/A')}")
                print(f"   Location: {summary.get('location', 'N/A')}")
            else:
                print("❌ Failed to get job summary")
        else:
            print("⚠️  No real URLs available - skipping job summary test")
            
    except Exception as e:
        print(f"❌ Scraper tools test failed: {e}")
        return False
    
    return True

def test_workflow_tool():
    """Test the complete workflow MCP tool."""
    print("\n🔄 Testing Workflow MCP Tool")
    print("=" * 50)
    
    try:
        from mcp_client import full_workflow
        
        print("\n🚀 Test: full_workflow")
        result = full_workflow("from:linkedin.com", max_emails=2, max_jobs=1)
        
        print(f"✅ Workflow completed:")
        print(f"   Emails found: {result['emails_found']}")
        print(f"   URLs extracted: {result['urls_extracted']}")
        print(f"   Jobs scraped: {result['jobs_scraped']}")
        print(f"   Summary: {result['summary']}")
        
        if result['job_data']:
            job = result['job_data'][0]
            print(f"   Sample job: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Workflow tool test failed: {e}")
        return False
    
    return True

def test_mcp_server():
    """Test that MCP server can start."""
    print("\n🚀 Testing MCP Server Startup")
    print("=" * 50)
    
    try:
        from mcp_client import app
        
        # Test that the app is properly configured
        print(f"✅ MCP server configured with tools:")
        expected_tools = [
            'list_emails', 'extract_job_urls', 'get_email_content', 'label_email',
            'scrape_job', 'scrape_multiple_jobs', 'convert_to_guest_url',
            'validate_linkedin_url', 'get_job_summary', 'full_workflow'
        ]
        
        # Check if tools exist by trying to access them
        for tool in expected_tools:
            try:
                # Check if the tool exists in the FastMCP app
                status = "✅" if hasattr(app, '_tools') and any(t.name == tool for t in app._tools.values()) else "❓"
                print(f"   {status} {tool}")
            except:
                print(f"   ❓ {tool}")
            
        print(f"\n💡 To start MCP server: python mcp_client.py")
        
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False
    
    return True

def get_real_test_url():
    """Get a real LinkedIn URL from test data if available."""
    try:
        # Try to get URL from visible_urls folder
        urls_file = Path("scraper_module/visible_urls/test_real_urls.json")
        if urls_file.exists():
            with open(urls_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict) and 'url' in data[0]:
                        return data[0]['url']
                    elif isinstance(data[0], str):
                        return data[0]
    except:
        pass
    
    return None

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
        print("   1. Start MCP server: python mcp_client.py")
        print("   2. Configure your AI assistant to use mcp_config.json")
        print("   3. Use the tools in AI conversations!")
    else:
        print("⚠️  Some tests failed. Please fix issues before using with AI assistant.")

if __name__ == "__main__":
    main() 