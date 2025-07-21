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
    """Test that list_emails properly displays email results."""
    print("🧪 Testing Email Display Functionality")
    print("=" * 50)
    
    # Test both modes
    modes = [
        ("Local Mode", False),
        ("MCP Client Mode", True)
    ]
    
    for mode_name, use_mcp_client in modes:
        print(f"\n🔧 Testing {mode_name}")
        print("-" * 30)
        
        try:
            # Initialize host
            host = OpenAILLMHost(use_mcp_client=use_mcp_client)
            
            # Simulate user asking for email list
            user_message = "Can you list the most recent 3 emails from LinkedIn?"
            
            print(f"🗣️  User: {user_message}")
            print(f"🤔 AI is thinking and using tools...")
            
            # Process the message
            response = await host.chat(user_message)
            
            print(f"\n🤖 AI Assistant Response:")
            print(f"{response}")
            
            # Check if the response contains actual email details
            has_email_details = any(keyword in response.lower() for keyword in [
                'subject:', 'from:', 'date:', 'id:', 'linkedin job alerts'
            ])
            
            if has_email_details:
                print(f"\n✅ {mode_name}: Email details properly displayed")
            else:
                print(f"\n❌ {mode_name}: Email details NOT displayed")
                print(f"   Response only contains: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ Error in {mode_name}: {e}")
        
        finally:
            # Cleanup
            if use_mcp_client:
                try:
                    await host.cleanup()
                except:
                    pass
        
        print("\n" + "="*50)

async def test_direct_tool_call():
    """Test direct tool execution to verify the fix."""
    print("\n🔧 Testing Direct Tool Execution")
    print("-" * 30)
    
    # Test MCP mode
    host = OpenAILLMHost(use_mcp_client=True)
    
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