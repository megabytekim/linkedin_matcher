#!/usr/bin/env python3
"""
OpenAI LLM Host for LinkedIn Job Scraper

This implements the GPT-4 host that can use either:
1. MCP Client (network boundary, JSON-RPC) - for production
2. Local functions (direct import) - for development/demos

Architecture options:
- Option 1: User Chat ↔ OpenAI GPT-4 ↔ MCP Client ↔ MCP Server ↔ Tools
- Option 2: User Chat ↔ OpenAI GPT-4 ↔ Local Tools (direct import)
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import openai
from openai import OpenAI

class OpenAILLMHost:
    """
    OpenAI GPT-4 host with flexible backend options.
    
    Can use either:
    1. MCP Client for network-based tool calls
    2. Local function imports for direct calls
    """
    
    def __init__(self, api_key: Optional[str] = None, use_mcp_client: bool = False):
        """
        Initialize the OpenAI LLM Host.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            use_mcp_client: If True, use MCP client. If False, use local functions.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.use_mcp_client = use_mcp_client
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        
        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        
        # Session memory for storing tool results and intermediate data
        self.session_memory = {
            'emails': {},  # email_id -> email_data
            'job_urls': {},  # email_id -> [urls]
            'scraped_jobs': {},  # url -> job_data
            'workflow_results': [],  # Complete workflow results
            'last_query': None,  # Last Gmail query used
            'last_emails_found': 0  # Number of emails found in last search
        }
        
        # Initialize tools based on mode
        if use_mcp_client:
            self._init_mcp_client()
        else:
            self._init_local_tools()
        
        self.system_prompt = self._create_system_prompt()
        self.mcp_tools = self._define_mcp_tools()
    
    def _init_mcp_client(self):
        """Initialize MCP client for network-based tool calls."""
        from .mcp_client import MCPClient
        
        # Initialize MCP client with server command
        self.mcp_client = MCPClient(
            server_command=["python", "core/serve.py"],
            cwd=str(Path(__file__).parent.parent)  # Project root
        )
        
        print("📡 MCP Client mode (network boundary)")
        self.tool_mode = "mcp_client"
        
        # Note: MCP client will be started when first tool call is made
        self._mcp_client_started = False
    
    def _init_local_tools(self):
        """Initialize local function imports for direct tool calls."""
        from core.tools.gmail import (
            list_emails, extract_job_urls, get_message_content,
            add_label, get_job_details_from_email
        )
        from core.tools.scraper import (
            scrape_job, scrape_job_async, scrape_multiple_jobs, convert_to_guest_url,
            validate_linkedin_url, get_job_summary
        )
        
        # Define local tools
        self.local_tools = {
            'list_emails': list_emails,
            'extract_job_urls': extract_job_urls,
            'get_message_content': get_message_content,
            'add_label': add_label,
            'get_job_details_from_email': get_job_details_from_email,
            'scrape_job': scrape_job,
            'scrape_job_async': scrape_job_async,
            'scrape_multiple_jobs': scrape_multiple_jobs,
            'convert_to_guest_url': convert_to_guest_url,
            'validate_linkedin_url': validate_linkedin_url,
            'get_job_summary': get_job_summary
        }
        
        print("🔧 Local tools mode (direct import)")
        self.tool_mode = "local"
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM."""
        # Get current memory status
        memory_summary = self.get_memory_summary()
        
        return f"""You are a LinkedIn Job Search Assistant with access to powerful tools for Gmail and LinkedIn job scraping.

Current Session Memory: {memory_summary}
Tool Mode: {self.tool_mode}

Your capabilities:
- Search Gmail for job-related emails using any Gmail search query
- Extract job URLs from emails  
- Scrape LinkedIn job postings for complete details
- Analyze and recommend job opportunities
- Apply labels to emails for organization

**Gmail Search Guidelines:**
- The `list_emails(query, max_results)` tool can take any Gmail search query.
- If `query` is omitted or empty, it will return the most recent emails from all senders.
- If `query` is provided, it will filter emails using that query (e.g., `from:linkedin.com`, `from:naver.com`, `subject:면접`, `label:INBOX`).
- Always show only the top 5~10 emails in your response. If the user wants to see more, offer to show additional emails.
- Example queries:
  - `from:linkedin.com` (LinkedIn job alerts)
  - `from:naver.com` (Naver emails)
  - `subject:면접` (emails with '면접' in the subject)
  - `label:INBOX` (all inbox emails)
  - `from:daum.net` (Daum emails)

CRITICAL DISPLAY GUIDELINES:
1. **ALWAYS SHOW TOOL RESULTS TO THE USER** - Don't just say "I found X emails"
2. **FORMAT EMAIL LISTS** clearly with:
   - Email subject (truncated if needed)
   - Sender information  
   - Date/time
   - Email ID for reference
3. **DISPLAY JOB URLS** when extracted from emails
4. **SHOW SCRAPED JOB DETAILS** in organized format
5. **BE TRANSPARENT** about what tools you're using and what data you're processing

IMPORTANT WORKFLOW GUIDELINES:
1. When asked to find and scrape jobs, follow this exact sequence:
   a) Use list_emails() to search for job-related emails
   b) **DISPLAY the email list to the user** (show only the top 5~10)
   c) For each email found, use extract_job_urls() with the ACTUAL email_id from step a
   d) **SHOW the extracted URLs to the user**
   e) For each URL extracted, use scrape_job() to get complete details
   f) **PRESENT the scraped job details in organized format**
   
2. ALWAYS use REAL email IDs from list_emails() results - never make up IDs like "latest_email_id_1"

3. For complex requests like "find emails and scrape jobs", break them down into steps:
   - First: Search emails and SHOW the list (top 5~10)
   - Second: Extract URLs from found emails and DISPLAY them
   - Third: Scrape jobs from extracted URLs and PRESENT results

4. When multiple emails are found, process them systematically:
   - Show the complete email list first (top 5~10)
   - Extract URLs from each email individually  
   - Display progress as you work through each email
   - Scrape each job URL found
   - Provide a comprehensive summary

5. If you already have emails in memory, you can reference them:
   - "I found X emails earlier, here they are again:"
   - "Based on the emails we found, here are the job opportunities:"

6. **RECOMMENDED**: For complex requests like "find emails and scrape all jobs", use the auto_job_search_workflow() tool which handles the entire process automatically and correctly.

7. **CRITICAL**: When using individual tools, always copy the exact email_id and URL values from previous tool results - never invent or simplify them.

RESPONSE FORMAT EXAMPLES:

For list_emails:
```
📧 Found 3 LinkedIn job emails:

1. **"5 new jobs for software"**
   From: LinkedIn Job Alerts <jobalerts-noreply@linkedin.com>
   Date: Mon, 21 Jul 2025 06:57:09 +0000 (UTC)
   ID: 1982bc5ac51ec213

2. **"Machine Learning Engineer: CLO Virtual Fashion"** 
   From: LinkedIn Job Alerts <jobalerts-noreply@linkedin.com>
   Date: Mon, 21 Jul 2025 04:57:08 +0000 (UTC)
   ID: 1982b57d33701719

[Continue for all emails...]
```

For extract_job_urls:
```
🔗 Extracted job URLs from email "5 new jobs for software":
• https://www.linkedin.com/jobs/view/3842851234/
• https://www.linkedin.com/jobs/view/3842851235/
• https://www.linkedin.com/jobs/view/3842851236/
```

Key principles:
1. Always be helpful and provide actionable insights
2. Use specific tools for specific tasks (don't guess)
3. **ALWAYS DISPLAY tool results clearly to the user**
4. Provide clear, formatted responses with job details
5. Ask for clarification when queries are ambiguous
6. Explain what you're doing and why
7. Handle errors gracefully and suggest alternatives
8. Use actual data from previous tool calls - never invent IDs or data

When users ask about jobs:
1. First search their Gmail for relevant emails and SHOW the list (top 5~10)
2. Extract job URLs from those emails using REAL email IDs and DISPLAY URLs
3. Scrape the most promising job postings and PRESENT details
4. Present results in a clear, organized format
5. Offer to perform additional analysis or actions

Available tools depend on mode:
- Local mode: Direct function calls for fastest performance
- MCP mode: Network calls for proper separation of concerns

Be conversational, helpful, and proactive in suggesting next steps. Most importantly: **ALWAYS SHOW THE ACTUAL DATA TO THE USER** rather than just mentioning that you found it."""

    def _define_mcp_tools(self) -> List[Dict[str, Any]]:
        """Define tools for OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_emails",
                    "description": "Search Gmail for messages matching a query (e.g., LinkedIn job emails)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Gmail search query (e.g., 'from:linkedin.com data science')"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of emails to return (1-50)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "extract_job_urls",
                    "description": "Extract LinkedIn job URLs from a specific email",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email_id": {
                                "type": "string",
                                "description": "Gmail message ID"
                            }
                        },
                        "required": ["email_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "scrape_job",
                    "description": "Scrape a single LinkedIn job posting for complete details",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "LinkedIn job URL to scrape"
                            },
                            "max_content_length": {
                                "type": "integer",
                                "description": "Maximum length for description content",
                                "default": 2000
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "auto_job_search_workflow",
                    "description": "Complete automated workflow: Search emails → Extract URLs → Scrape jobs → Return comprehensive results",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Gmail search query (e.g., 'from:linkedin.com', '채용공고')",
                                "default": "from:linkedin.com OR 채용공고 OR job"
                            },
                            "max_emails": {
                                "type": "integer",
                                "description": "Maximum emails to process",
                                "default": 5
                            },
                            "max_jobs": {
                                "type": "integer", 
                                "description": "Maximum jobs to scrape",
                                "default": 10
                            }
                        },
                        "required": []
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool using the configured backend (MCP client or local)."""
        try:
            print(f"🔧 Executing tool: {tool_name} with args: {kwargs}")
            
            if self.use_mcp_client:
                # Start MCP client if not already started
                if not self._mcp_client_started:
                    print("🚀 Starting MCP client...")
                    await self.mcp_client.start()
                    self._mcp_client_started = True
                
                # Map OpenAI function names to MCP tool names
                mcp_tool_name = self._map_to_mcp_tool_name(tool_name)
                
                # Call tool via MCP client
                result = await self.mcp_client.call_tool(mcp_tool_name, kwargs)
                
                # Process MCP result format
                processed_result = self._process_mcp_result(result)
                
                # Store results in session memory based on tool type
                self._store_tool_result_in_memory(tool_name, processed_result, kwargs)
                
                return processed_result
            else:
                # Use local functions
                if tool_name == "list_emails":
                    result = self.local_tools['list_emails'](kwargs.get('query', ''), kwargs.get('max_results', 10))
                    # Store emails in memory
                    for email in result:
                        self.session_memory['emails'][email['id']] = email
                    return result
                
                elif tool_name == "extract_job_urls":
                    result = self.local_tools['extract_job_urls'](kwargs['email_id'])
                    self.session_memory['job_urls'][kwargs['email_id']] = result
                    return result
                
                elif tool_name == "scrape_job":
                    url = kwargs['url']
                    result = await self.local_tools['scrape_job_async'](url, kwargs.get('max_content_length', 2000))
                    if result:
                        self.session_memory['scraped_jobs'][url] = result
                    return result
                
                elif tool_name == "auto_job_search_workflow":
                    return await self._execute_auto_workflow(
                        kwargs.get('query', 'from:linkedin.com OR 채용공고 OR job'),
                        kwargs.get('max_emails', 5),
                        kwargs.get('max_jobs', 10)
                    )
                
                else:
                    return f"Unknown tool: {tool_name}"
                
        except Exception as e:
            print(f"❌ Error executing tool {tool_name}: {e}")
            return f"Error: {str(e)}"
    
    def _process_mcp_result(self, result: Any) -> Any:
        """Process MCP result format to extract the actual data."""
        if isinstance(result, dict) and 'content' in result:
            content_items = result.get('content', [])
            if content_items and isinstance(content_items, list):
                # Try to parse each content item and collect results
                parsed_items = []
                
                for item in content_items:
                    if item.get('type') == 'text':
                        text_content = item.get('text', '{}')
                        try:
                            parsed_item = json.loads(text_content)
                            parsed_items.append(parsed_item)
                        except json.JSONDecodeError:
                            # If it's not JSON, return the text as-is
                            parsed_items.append(text_content)
                
                # If we have multiple items, return as list; single item, return the item itself
                if len(parsed_items) == 1:
                    return parsed_items[0]
                elif len(parsed_items) > 1:
                    return parsed_items
                else:
                    return content_items
            return result.get('content', {})
        
        return result
    
    def _store_tool_result_in_memory(self, tool_name: str, result: Any, kwargs: dict) -> None:
        """Store tool results in session memory for future reference."""
        try:
            if tool_name == "list_emails" and isinstance(result, list):
                # Store emails in memory
                for email in result:
                    if isinstance(email, dict) and 'id' in email:
                        self.session_memory['emails'][email['id']] = email
                print(f"💾 Stored {len(result)} emails in session memory")
                
            elif tool_name == "extract_job_urls":
                email_id = kwargs.get('email_id')
                if email_id and result:
                    self.session_memory['job_urls'][email_id] = result
                    print(f"💾 Stored job URLs for email {email_id} in session memory")
                    
            elif tool_name == "scrape_job":
                url = kwargs.get('url')
                if url and result:
                    self.session_memory['scraped_jobs'][url] = result
                    print(f"💾 Stored scraped job data for {url} in session memory")
                    
        except Exception as e:
            print(f"⚠️  Warning: Failed to store result in memory: {e}")
    
    def _map_to_mcp_tool_name(self, openai_function_name: str) -> str:
        """Map OpenAI function names to MCP tool names."""
        # OpenAI function names → MCP tool names
        mapping = {
            "list_emails": "mcp_list_emails",
            "extract_job_urls": "mcp_extract_job_urls", 
            "scrape_job": "mcp_scrape_job",
            "auto_job_search_workflow": "full_workflow"
        }
        return mapping.get(openai_function_name, openai_function_name)
    
    async def _execute_auto_workflow(self, query: str, max_emails: int, max_jobs: int) -> dict:
        """Execute complete automated job search workflow."""
        try:
            print(f"🔄 Starting auto workflow: {query}")
            
            # Step 1: Search emails
            emails = self.local_tools['list_emails'](query, max_emails)
            if not emails:
                return {
                    'status': 'no_emails_found',
                    'message': f'No emails found for query: {query}',
                    'emails_found': 0,
                    'urls_extracted': 0,
                    'jobs_scraped': 0
                }
            
            # Store emails in memory
            for email in emails:
                self.session_memory['emails'][email['id']] = email
            
            # Step 2: Extract URLs from all emails
            all_urls = []
            for email in emails:
                try:
                    urls = self.local_tools['extract_job_urls'](email['id'])
                    self.session_memory['job_urls'][email['id']] = urls
                    all_urls.extend([url_info['url'] for url_info in urls if 'url' in url_info])
                except Exception as e:
                    print(f"Failed to extract URLs from email {email['id']}: {e}")
            
            # Step 3: Scrape jobs (limit to max_jobs)
            urls_to_scrape = all_urls[:max_jobs]
            scraped_jobs = []
            
            for url in urls_to_scrape:
                try:
                    job_data = await self.local_tools['scrape_job_async'](url)
                    if job_data:
                        scraped_jobs.append(job_data)
                        self.session_memory['scraped_jobs'][url] = job_data
                except Exception as e:
                    print(f"Failed to scrape {url}: {e}")
            
            # Step 4: Store workflow result
            workflow_result = {
                'query': query,
                'emails_found': len(emails),
                'urls_extracted': len(all_urls),
                'jobs_scraped': len(scraped_jobs),
                'emails': emails,
                'job_urls': all_urls,
                'scraped_jobs': scraped_jobs,
                'summary': f"Found {len(emails)} emails, extracted {len(all_urls)} URLs, scraped {len(scraped_jobs)} jobs"
            }
            
            self.session_memory['workflow_results'].append(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            print(f"❌ Auto workflow failed: {e}")
            return {
                'status': 'error',
                'message': f'Workflow failed: {str(e)}',
                'emails_found': 0,
                'urls_extracted': 0,
                'jobs_scraped': 0
            }
    
    async def chat(self, user_message: str) -> str:
        """Process a user message through OpenAI GPT-4 with tool access."""
        try:
            # Add user message to conversation
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history,
                {"role": "user", "content": user_message}
            ]
            
            print(f"🤖 Processing with GPT-4: {user_message[:50]}...")
            
            # Call OpenAI with tool access
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.mcp_tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2000
            )
            
            assistant_message = response.choices[0].message
            
            # Handle tool calls if any
            if assistant_message.tool_calls:
                print(f"🔧 GPT-4 wants to use {len(assistant_message.tool_calls)} tools")
                
                # Execute all tool calls
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the tool
                    result = await self.execute_tool(function_name, **function_args)
                    
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result, default=str)
                    })
                
                # Get final response with tool results
                final_messages = messages + [
                    assistant_message,
                    *tool_results
                ]
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=final_messages,
                    temperature=0.7,
                    max_tokens=2000
                )
                
                final_content = final_response.choices[0].message.content
            else:
                final_content = assistant_message.content
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": final_content}
            ])
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return final_content
            
        except Exception as e:
            print(f"❌ Error in chat: {e}")
            return f"I encountered an error: {str(e)}. Please try again or rephrase your question."
    
    def get_memory_summary(self) -> str:
        """Get a summary of current session memory."""
        summary = []
        if self.session_memory['emails']:
            summary.append(f"📧 {len(self.session_memory['emails'])} emails cached")
        if self.session_memory['job_urls']:
            total_urls = sum(len(urls) for urls in self.session_memory['job_urls'].values())
            summary.append(f"🔗 {total_urls} job URLs extracted")
        if self.session_memory['scraped_jobs']:
            summary.append(f"💼 {len(self.session_memory['scraped_jobs'])} jobs scraped")
        if self.session_memory['workflow_results']:
            summary.append(f"🔄 {len(self.session_memory['workflow_results'])} workflows completed")
        
        return " | ".join(summary) if summary else "No data in memory"
    
    def save_conversation(self):
        """Save conversation history to file."""
        try:
            history_file = Path("host/openai_conversation_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2, default=str)
            print(f"💾 Conversation saved to {history_file}")
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def save_session_memory(self):
        """Save session memory to file."""
        try:
            memory_file = Path("host/openai_session_memory.json")
            with open(memory_file, 'w') as f:
                json.dump(self.session_memory, f, indent=2, default=str)
            print(f"💾 Session memory saved to {memory_file}")
        except Exception as e:
            print(f"❌ Error saving session memory: {e}")

    async def cleanup(self):
        """Clean up resources, especially MCP client."""
        if self.use_mcp_client and hasattr(self, 'mcp_client') and self._mcp_client_started:
            print("🧹 Cleaning up MCP client...")
            await self.mcp_client.stop()
            self._mcp_client_started = False
            print("✅ MCP client cleanup complete")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        if self.use_mcp_client and hasattr(self, 'mcp_client') and self._mcp_client_started:
            # Note: Can't use async in __del__, so this is just a warning
            print("⚠️  MCP client was not properly cleaned up. Use await host.cleanup()")


async def main():
    """Main chat interface for OpenAI LLM Host."""
    print("🚀 LinkedIn Job Assistant - OpenAI + Tools Integration")
    print("=" * 70)
    print("🎯 GPT-4 powered job search with tools")
    print("💬 Ask natural language questions about your job search")
    print("❓ Type 'quit' to exit")
    print("=" * 70)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("💡 Please set OPENAI_API_KEY environment variable:")
        print("   export OPENAI_API_KEY='sk-your-key-here'")
        return
    
    # Initialize host (use local tools by default)
    try:
        host = OpenAILLMHost(api_key, use_mcp_client=False)
        print("✅ OpenAI LLM Host initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    print("\n🤖 Ready! Ask me anything about your job search...")
    print("💡 Examples:")
    print("   • 'Find data science jobs in my emails'")
    print("   • 'What are the latest machine learning opportunities?'")
    print("   • 'Scrape the most recent job postings and summarize them'\n")
    
    while True:
        try:
            # Get user input
            user_input = input("🗣️  You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for using LinkedIn Job Assistant!")
                host.save_conversation()
                host.save_session_memory()
                break
            
            # Check for memory status
            if user_input.lower() in ['memory', 'mem', '상태']:
                memory_summary = host.get_memory_summary()
                print(f"\n🧠 Session Memory Status: {memory_summary}")
                continue
            
            # Process with OpenAI + Tools
            print("\n🤔 AI is thinking and using tools...")
            response = await host.chat(user_input)
            
            # Display response
            print(f"\n🤖 AI Assistant:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using LinkedIn Job Assistant!")
            host.save_conversation()
            host.save_session_memory()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    asyncio.run(main()) 