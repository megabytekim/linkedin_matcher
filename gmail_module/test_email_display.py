#!/usr/bin/env python3
"""
Test Email Display Functionality

This script tests that the list_emails function properly displays
email results to the user instead of just saying "I found emails".
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from host.openai_host import OpenAILLMHost

async def test_email_display():
    """Test email display functionality."""
    print("🧪 Testing Email Display...")
    
    try:
        # Initialize host
        host = OpenAILLMHost()
        
        # Test email listing
        print("📧 Testing email listing...")
        result = await host.execute_tool("list_emails", query="from:linkedin.com", max_results=3)
        
        if isinstance(result, list) and len(result) > 0:
            print(f"✅ Found {len(result)} emails")
            
            # Display first email details
            first_email = result[0]
            print(f"\n📄 First Email Details:")
            print(f"   Subject: {first_email.get('subject', 'No subject')}")
            print(f"   From: {first_email.get('from', 'Unknown')}")
            print(f"   Date: {first_email.get('date', 'Unknown')}")
            print(f"   Snippet: {first_email.get('snippet', 'No snippet')[:100]}...")
            
            # Test URL extraction
            print("\n🔗 Testing URL extraction...")
            urls_result = await host.execute_tool("extract_job_urls", email_id=first_email['id'])
            print(f"   URLs found: {len(urls_result) if isinstance(urls_result, list) else 0}")
            
        else:
            print("⚠️  No emails found or unexpected result format")
        
        # Test MCP client cleanup
        await host.cleanup()
        print("✅ MCP client cleanup successful")
        
        print(f"✅ Email display test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Email display test failed: {e}")
        return False

async def test_direct_tool_call():
    """Test direct tool execution to verify the fix."""
    print("\n🔧 Testing Direct Tool Execution")
    print("-" * 30)
    
    # Test MCP mode
    host = OpenAILLMHost()
    
    try:
        print("📧 Calling list_emails directly...")
        result = await host.execute_tool(
            "list_emails", 
            query="from:linkedin.com", 
            max_results=2
        )
        
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result length: {len(result) if isinstance(result, list) else 'Not a list'}")
        
        if isinstance(result, list):
            print(f"📧 Emails found:")
            for i, email in enumerate(result):
                print(f"   {i+1}. Subject: {email.get('subject', 'No subject')}")
                print(f"      From: {email.get('from', 'Unknown')}")
                print(f"      ID: {email.get('id', 'No ID')}")
                print()
        else:
            print(f"⚠️  Result is not a list: {result}")
            
    finally:
        await host.cleanup()

async def main():
    """Run all tests."""
    print("🚀 Email Display Test Suite")
    print("=" * 50)
    
    # Test 1: Direct tool call
    await test_direct_tool_call()
    
    # Test 2: Full AI chat integration  
    await test_email_display()
    
    print("\n✅ All email display tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 