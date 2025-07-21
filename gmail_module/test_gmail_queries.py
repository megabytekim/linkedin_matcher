#!/usr/bin/env python3
"""
Test list_emails with various queries to verify filtering and result formatting.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from host.openai_host import OpenAILLMHost

async def test_queries():
    host = OpenAILLMHost(use_mcp_client=True)
    try:
        for query in [
            '',
            'from:linkedin.com',
            'from:naver.com',
            'subject:면접',
            'from:daum.net'
        ]:
            print(f'\n===== QUERY: {query or "(all emails)"} =====')
            result = await host.execute_tool('list_emails', query=query, max_results=10)
            if isinstance(result, list):
                for i, email in enumerate(result[:10]):
                    print(f'{i+1}. {email.get("subject", "No subject")} | {email.get("from", "No from")} | {email.get("date", "No date")}')
            else:
                print(result)
    finally:
        await host.cleanup()

if __name__ == "__main__":
    asyncio.run(test_queries()) 