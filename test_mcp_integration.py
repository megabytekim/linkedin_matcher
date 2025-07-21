#!/usr/bin/env python3
"""
Test MCP Client Integration with OpenAI Host

This script tests the complete MCP Client → MCP Server integration
using the OpenAI Host.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from host.openai_host import OpenAILLMHost

async def test_mcp_integration():
    """Test MCP Client integration with real tool calls."""
    print("🧪 Testing MCP Client Integration")
    print("=" * 50)
    
    # Test both modes for comparison
    modes = [
        ("Local Mode", False),  # Direct import
        ("MCP Client Mode", True)  # MCP Client → MCP Server
    ]
    
    for mode_name, use_mcp_client in modes:
        print(f"\n🔧 Testing {mode_name}")
        print("-" * 30)
        
        try:
            # Initialize host
            host = OpenAILLMHost(use_mcp_client=use_mcp_client)
            
            # Test tool execution
            print("📧 Testing list_emails tool...")
            result = await host.execute_tool(
                "list_emails",
                query="from:linkedin.com",
                max_results=2
            )
            
            if isinstance(result, list):
                print(f"✅ Found {len(result)} emails")
                for i, email in enumerate(result[:2]):
                    print(f"   {i+1}. {email.get('subject', 'No subject')[:50]}...")
            else:
                print(f"📄 Result: {str(result)[:100]}...")
            
            print()
            
        except Exception as e:
            print(f"❌ Error in {mode_name}: {e}")
        
        finally:
            # Cleanup
            if use_mcp_client:
                try:
                    await host.cleanup()
                except:
                    pass

async def test_mcp_client_only():
    """Test MCP Client directly (without OpenAI Host)."""
    print("\n🔧 Testing MCP Client Only")
    print("-" * 30)
    
    from host.mcp_client import MCPClient
    
    client = MCPClient(["python", "core/serve.py"])
    
    try:
        await client.start()
        
        # List tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {len(tools)}")
        
        # Test a tool
        if tools:
            result = await client.call_tool("mcp_list_emails", {
                "query": "from:linkedin.com",
                "max_results": 2
            })
            print(f"📧 Tool result type: {type(result)}")
            print(f"📧 Tool result: {str(result)[:200]}...")
    
    except Exception as e:
        print(f"❌ MCP Client error: {e}")
    
    finally:
        await client.stop()

async def main():
    """Run all tests."""
    print("🚀 MCP Integration Test Suite")
    print("=" * 50)
    
    # Test 1: MCP Client only
    await test_mcp_client_only()
    
    # Test 2: OpenAI Host integration
    await test_mcp_integration()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 