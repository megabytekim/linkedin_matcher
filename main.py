#!/usr/bin/env python3
"""
LinkedIn Job Matcher - Main Launcher

This is the main entry point for the LinkedIn Job Matcher application.
It provides both Local and MCP Client modes for different use cases.

Usage:
    python main.py --mode local      # Direct function calls (faster, development)
    python main.py --mode mcp        # MCP Client-Server (production, scalable)
    python main.py --test            # Run integration tests
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="LinkedIn Job Matcher - AI-powered job search assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode local      # Use local mode (direct function calls)
  python main.py --mode mcp        # Use MCP Client-Server mode
  python main.py --test            # Run integration tests
  python main.py --help            # Show this help message

Modes:
  local     Direct function calls (faster, good for development)
  mcp       MCP Client-Server architecture (scalable, production-ready)
  
For first-time setup:
  1. Set OPENAI_API_KEY environment variable
  2. Set up Gmail API credentials (credentials.json)
  3. Run: python main.py --mode local
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['local', 'mcp'],
        default='local',
        help='Execution mode: local (direct) or mcp (client-server)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run integration tests instead of starting chat interface'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Run tests if requested
    if args.test:
        print("🧪 Running integration tests...")
        return asyncio.run(run_tests())
    
    # Check environment
    if not check_environment():
        return 1
    
    # Start the application
    use_mcp_client = (args.mode == 'mcp')
    
    print(f"🚀 Starting LinkedIn Job Matcher in {args.mode.upper()} mode")
    print("=" * 60)
    
    return asyncio.run(start_application(use_mcp_client))

def check_environment():
    """Check if environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("💡 Please set it with: export OPENAI_API_KEY='sk-your-key-here'")
        return False
    
    # Check Gmail credentials
    if not Path('credentials.json').exists() and not Path('token.json').exists():
        print("⚠️  Gmail API credentials not found!")
        print("💡 Please set up Gmail API credentials:")
        print("   1. Go to Google Cloud Console")
        print("   2. Enable Gmail API")
        print("   3. Download credentials.json")
        print("   4. Place it in the project root")
        print("   (The app will still work but Gmail features will be limited)")
    
    print("✅ Environment check completed")
    return True

async def start_application(use_mcp_client: bool):
    """Start the main application."""
    try:
        from host.openai_host import OpenAILLMHost
        
        # Initialize host
        host = OpenAILLMHost(use_mcp_client=use_mcp_client)
        
        mode_name = "MCP Client-Server" if use_mcp_client else "Local Direct"
        print(f"✅ {mode_name} mode initialized successfully!")
        
        # Start chat interface
        await run_chat_interface(host)
        
        # Cleanup
        if use_mcp_client:
            await host.cleanup()
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return 1

async def run_chat_interface(host):
    """Run the interactive chat interface."""
    print("\n🤖 AI Assistant ready! Ask me about job search...")
    print("💡 Examples:")
    print("   • 'Find data science jobs in my emails'")
    print("   • 'What are the latest machine learning opportunities?'")
    print("   • 'Scrape and summarize recent job postings'")
    print("❓ Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("🗣️  You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for using LinkedIn Job Matcher!")
                host.save_conversation()
                host.save_session_memory()
                break
                
            if user_input.lower() in ['memory', 'status']:
                memory = host.get_memory_summary()
                print(f"\n🧠 Memory: {memory}\n")
                continue
            
            # Process message
            print("\n🤔 AI is thinking and using tools...")
            response = await host.chat(user_input)
            print(f"\n🤖 AI Assistant:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using LinkedIn Job Matcher!")
            host.save_conversation()
            host.save_session_memory()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

async def run_tests():
    """Run integration tests."""
    try:
        from test_mcp_integration import main as test_main
        await test_main()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 