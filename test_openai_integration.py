#!/usr/bin/env python3
"""
Test OpenAI LLM Host Integration

This script tests the OpenAI LLM Host implementation to ensure
all components are properly configured and can be imported.
"""

import os
import sys
import asyncio
from unittest.mock import patch, MagicMock


def test_imports():
    """Test that all required modules can be imported."""
    print("🔧 Testing imports...")
    
    try:
        # Test OpenAI import
        import openai
        from openai import OpenAI
        print("  ✅ OpenAI library imported successfully")
        
        # Test MCP tools import
        from mcp_tools.gmail_tools import list_emails, extract_job_urls
        from mcp_tools.scraper_tools import scrape_job, get_job_summary
        print("  ✅ MCP tools imported successfully")
        
        # Test main host class import (without initialization)
        from openai_llm_host import OpenAILLMHost
        print("  ✅ OpenAILLMHost class imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def test_mcp_tool_definitions():
    """Test that MCP tool definitions are properly structured."""
    print("\n🛠️  Testing MCP tool definitions...")
    
    try:
        # Import with mock to avoid API key requirement
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            from openai_llm_host import OpenAILLMHost
            
            # Mock the OpenAI client to avoid API calls
            with patch('openai_llm_host.OpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client
                
                host = OpenAILLMHost()
                tools = host.mcp_tools
                
                print(f"  ✅ Found {len(tools)} MCP tools defined")
                
                # Check tool structure
                required_fields = ['type', 'function']
                for i, tool in enumerate(tools):
                    if not all(field in tool for field in required_fields):
                        print(f"  ❌ Tool {i} missing required fields")
                        return False
                    
                    func = tool['function']
                    if not all(field in func for field in ['name', 'description', 'parameters']):
                        print(f"  ❌ Tool {i} function missing required fields")
                        return False
                
                print("  ✅ All tool definitions are properly structured")
                
                # List available tools
                tool_names = [tool['function']['name'] for tool in tools]
                print(f"  📋 Available tools: {', '.join(tool_names)}")
                
                return True
                
    except Exception as e:
        print(f"  ❌ Error testing tool definitions: {e}")
        return False


def test_tool_execution_interface():
    """Test that tool execution interface works without making API calls."""
    print("\n⚙️  Testing tool execution interface...")
    
    try:
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            from openai_llm_host import OpenAILLMHost
            
            with patch('openai_llm_host.OpenAI') as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client
                
                host = OpenAILLMHost()
                
                # Test that execute_mcp_tool method exists and has proper signature
                assert hasattr(host, 'execute_mcp_tool')
                assert hasattr(host, 'chat')
                
                print("  ✅ Tool execution interface is properly defined")
                return True
                
    except Exception as e:
        print(f"  ❌ Error testing tool execution: {e}")
        return False


def test_environment_setup():
    """Test environment setup and configuration."""
    print("\n🌍 Testing environment setup...")
    
    # Check if OpenAI key is available (optional)
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        if openai_key.startswith('sk-'):
            print("  ✅ Valid OpenAI API key format detected")
        else:
            print("  ⚠️  OpenAI API key doesn't start with 'sk-' (might be invalid)")
    else:
        print("  ℹ️  No OpenAI API key found (set OPENAI_API_KEY to test live)")
    
    # Check requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            if 'openai' in requirements:
                print("  ✅ OpenAI dependency found in requirements.txt")
            else:
                print("  ❌ OpenAI dependency missing from requirements.txt")
                return False
    except FileNotFoundError:
        print("  ❌ requirements.txt not found")
        return False
    
    return True


def test_documentation():
    """Test that documentation files are updated."""
    print("\n📚 Testing documentation...")
    
    # Check README.md
    try:
        with open('README.md', 'r') as f:
            readme = f.read()
            if 'openai_llm_host.py' in readme:
                print("  ✅ README.md mentions OpenAI LLM Host")
            else:
                print("  ❌ README.md doesn't mention OpenAI LLM Host")
                return False
    except FileNotFoundError:
        print("  ❌ README.md not found")
        return False
    
    # Check project description
    try:
        with open('project_description.md', 'r') as f:
            desc = f.read()
            if 'OpenAI GPT-4' in desc:
                print("  ✅ project_description.md mentions OpenAI GPT-4")
            else:
                print("  ❌ project_description.md doesn't mention OpenAI GPT-4")
                return False
    except FileNotFoundError:
        print("  ❌ project_description.md not found")
        return False
    
    return True


async def main():
    """Run all tests."""
    print("🚀 Testing OpenAI LLM Host Integration")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_mcp_tool_definitions,
        test_tool_execution_interface,
        test_environment_setup,
        test_documentation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! OpenAI LLM Host is ready to use.")
        print("\n💡 Next steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='sk-your-key'")
        print("2. Run: python openai_llm_host.py")
        print("3. Ask natural language questions about job search!")
    else:
        print(f"❌ {total - passed} tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 