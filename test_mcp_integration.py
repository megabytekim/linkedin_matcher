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
    """Test MCP client-server integration."""
    print("🧪 Testing MCP Integration...")
    
    try:
        # Initialize host
        host = OpenAILLMHost()
        
        # Test basic functionality
        print("✅ Host initialized successfully")
        
        # Test tool execution
        print("🔧 Testing tool execution...")
        
        # Test list_emails tool
        result = await host.execute_tool("list_emails", query="from:linkedin.com", max_results=2)
        print(f"📧 List emails result: {type(result)} - {len(result) if isinstance(result, list) else 'N/A'}")
        
        # Test MCP client cleanup
        await host.cleanup()
        print("✅ MCP client cleanup successful")
        
        print(f"✅ MCP Client-Server mode test passed!")
        return True
        
    except Exception as e:
        print(f"❌ MCP Client-Server mode test failed: {e}")
        return False

async def test_mcp_client_only():
    """Test MCP Client directly (without OpenAI Host)."""
    print("\n🔧 Testing MCP Client Only")
    print("-" * 30)
    
    from host.mcp_client import MCPClient
    
    client = MCPClient(["python", "-m", "core.serve"])
    
    try:
        await client.start()
        
        # List tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {len(tools)}")
        
        # Test a tool
        if tools:
            result = await client.call_tool("list_emails", {
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
    success = await test_mcp_integration()
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 