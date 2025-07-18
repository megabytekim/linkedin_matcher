#!/usr/bin/env python3
"""
OpenAI LLM Host for LinkedIn Job Scraper

This implements the GPT-4 host that uses MCP (Model Context Protocol) tools
for Gmail and LinkedIn job scraping operations.

Architecture:
- User Chat ↔ OpenAI GPT-4 ↔ MCP Tools ↔ Gmail/Scraper Modules
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

# Import MCP tools directly
from mcp_tools.gmail_tools import list_emails, extract_job_urls, get_email_content, label_email, get_job_details_from_email
from mcp_tools.scraper_tools import scrape_job, scrape_multiple_jobs, convert_to_guest_url, validate_linkedin_url, get_job_summary


class OpenAILLMHost:
    """
    OpenAI GPT-4 host that uses MCP tools for LinkedIn job search operations.
    
    This class provides the bridge between natural language queries and
    our specialized MCP tools for Gmail and LinkedIn scraping.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI LLM Host.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Get model from environment or use default
        self.model = os.getenv('OPENAI_MODEL')
        
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
        
        self.system_prompt = self._create_system_prompt()
        
        # Define available MCP tools for OpenAI function calling
        self.mcp_tools = self._define_mcp_tools()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM."""
        # Get current memory status
        memory_summary = self.get_memory_summary()
        
        return f"""You are a LinkedIn Job Search Assistant with access to powerful tools for Gmail and LinkedIn job scraping.

Current Session Memory: {memory_summary}

Your capabilities:
- Search Gmail for LinkedIn job emails
- Extract job URLs from emails  
- Scrape LinkedIn job postings for complete details
- Analyze and recommend job opportunities
- Apply labels to emails for organization

IMPORTANT WORKFLOW GUIDELINES:
1. When asked to find and scrape jobs, follow this exact sequence:
   a) Use list_emails() to search for job-related emails
   b) For each email found, use extract_job_urls() with the ACTUAL email_id from step a
   c) For each URL extracted, use scrape_job() to get complete details
   
2. ALWAYS use REAL email IDs from list_emails() results - never make up IDs like "latest_email_id_1"

3. For complex requests like "find emails and scrape jobs", break them down into steps:
   - First: Search emails
   - Second: Extract URLs from found emails
   - Third: Scrape jobs from extracted URLs

4. When multiple emails are found, process them systematically:
   - Extract URLs from each email individually
   - Scrape each job URL found
   - Provide a comprehensive summary

5. If you already have emails in memory, you can reference them:
   - "I found X emails earlier, let me extract URLs from them"
   - "Based on the emails we found, here are the job opportunities"

6. **RECOMMENDED**: For complex requests like "find emails and scrape all jobs", use the auto_job_search_workflow() tool which handles the entire process automatically and correctly.

7. **CRITICAL**: When using individual tools, always copy the exact email_id and URL values from previous tool results - never invent or simplify them.

Key principles:
1. Always be helpful and provide actionable insights
2. Use specific tools for specific tasks (don't guess)
3. Provide clear, formatted responses with job details
4. Ask for clarification when queries are ambiguous
5. Explain what you're doing and why
6. Handle errors gracefully and suggest alternatives
7. Use actual data from previous tool calls - never invent IDs or data

When users ask about jobs:
1. First search their Gmail for relevant emails
2. Extract job URLs from those emails using REAL email IDs
3. Scrape the most promising job postings
4. Present results in a clear, organized format
5. Offer to perform additional analysis or actions

You have access to these MCP tools:
- list_emails: Search Gmail for job-related emails
- extract_job_urls: Get LinkedIn URLs from specific emails (use REAL email_id)
- get_email_content: Read full email content
- scrape_job: Scrape individual LinkedIn job postings
- scrape_multiple_jobs: Batch scrape multiple jobs
- get_job_summary: Quick overview of job postings
- label_email: Organize emails with labels
- Full workflow capabilities combining all operations

Be conversational, helpful, and proactive in suggesting next steps."""

    def _define_mcp_tools(self) -> List[Dict[str, Any]]:
        """Define MCP tools as OpenAI function calling tools."""
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
                    "name": "get_email_content", 
                    "description": "Get the full text content of an email",
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
                    "name": "scrape_multiple_jobs",
                    "description": "Scrape multiple LinkedIn job postings with rate limiting",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of LinkedIn job URLs to scrape"
                            },
                            "max_content_length": {
                                "type": "integer", 
                                "description": "Maximum length for description content",
                                "default": 1500
                            }
                        },
                        "required": ["urls"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_job_summary",
                    "description": "Get a quick summary of a job posting (title, company, location)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "LinkedIn job URL"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_linkedin_url",
                    "description": "Validate if a URL is a valid LinkedIn job URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to validate"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "label_email",
                    "description": "Apply a label to a Gmail message for organization",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email_id": {
                                "type": "string",
                                "description": "Gmail message ID"
                            },
                            "label": {
                                "type": "string",
                                "description": "Label name to apply"
                            }
                        },
                        "required": ["email_id", "label"]
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
    
    async def execute_mcp_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute an MCP tool and return the result."""
        try:
            print(f"🔧 Executing MCP tool: {tool_name} with args: {kwargs}")
            
            if tool_name == "list_emails":
                result = list_emails(kwargs.get('query', ''), kwargs.get('max_results', 10))
                # Store emails in memory
                for email in result:
                    self.session_memory['emails'][email['id']] = email
                self.session_memory['last_query'] = kwargs.get('query', '')
                self.session_memory['last_emails_found'] = len(result)
                
                # Format result to make email IDs more prominent
                formatted_result = {
                    'message': f'Found {len(result)} emails. Use these EXACT email IDs for further operations:',
                    'emails': result,
                    'email_ids': [email['id'] for email in result],
                    'instructions': 'IMPORTANT: Use the exact email_id values above for extract_job_urls() calls',
                    'example_usage': f"extract_job_urls(email_id='{result[0]['id']}') - Use exactly this format!" if result else 'No emails found'
                }
                return formatted_result
                
            elif tool_name == "extract_job_urls":
                email_id = kwargs['email_id']
                result = extract_job_urls(email_id)
                # Store job URLs in memory
                self.session_memory['job_urls'][email_id] = result
                
                # Format result to make URLs more prominent
                formatted_result = {
                    'message': f'Extracted job URLs from email {email_id}:',
                    'urls': result,
                    'url_list': [url_info['url'] for url_info in result if 'url' in url_info],
                    'instructions': 'Use these exact URLs for scrape_job() calls'
                }
                return formatted_result
                
            elif tool_name == "get_email_content":
                return get_email_content(kwargs['email_id'])
                
            elif tool_name == "scrape_job":
                url = kwargs['url']
                # Use async-compatible scraping
                from mcp_tools.scraper_tools import scrape_job_async
                result = await scrape_job_async(url, kwargs.get('max_content_length', 2000))
                # Store scraped job in memory
                if result:
                    self.session_memory['scraped_jobs'][url] = result
                return result
                
            elif tool_name == "scrape_multiple_jobs":
                urls = kwargs['urls']
                # Use async-compatible scraping
                from mcp_tools.scraper_tools import scrape_job_async
                results = []
                for url in urls:
                    try:
                        job_data = await scrape_job_async(url, kwargs.get('max_content_length', 1500))
                        if job_data:
                            results.append(job_data)
                            self.session_memory['scraped_jobs'][url] = job_data
                    except Exception as e:
                        print(f"Failed to scrape {url}: {e}")
                return results
                
            elif tool_name == "get_job_summary":
                return get_job_summary(kwargs['url'])
                
            elif tool_name == "validate_linkedin_url":
                return validate_linkedin_url(kwargs['url'])
                
            elif tool_name == "label_email":
                return label_email(kwargs['email_id'], kwargs['label'])
            elif tool_name == "auto_job_search_workflow":
                return await self._execute_auto_workflow(
                    kwargs.get('query', 'from:linkedin.com OR 채용공고 OR job'),
                    kwargs.get('max_emails', 5),
                    kwargs.get('max_jobs', 10)
                )
            else:
                return f"Unknown tool: {tool_name}"
                
        except Exception as e:
            print(f"❌ Error executing MCP tool {tool_name}: {e}")
            return f"Error: {str(e)}"
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message through OpenAI GPT-4 with MCP tool access.
        
        Args:
            user_message: User's natural language query
            
        Returns:
            AI response with tool results
        """
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
                    
                    # Execute the MCP tool
                    result = await self.execute_mcp_tool(function_name, **function_args)
                    
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
    
    def save_conversation(self):
        """Save conversation history to file."""
        try:
            history_file = Path("openai_conversation_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2, default=str)
            print(f"💾 Conversation saved to {history_file}")
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")
    
    def save_session_memory(self):
        """Save session memory to file."""
        try:
            memory_file = Path("openai_session_memory.json")
            with open(memory_file, 'w') as f:
                json.dump(self.session_memory, f, indent=2, default=str)
            print(f"💾 Session memory saved to {memory_file}")
        except Exception as e:
            print(f"❌ Error saving session memory: {e}")
    
    def load_session_memory(self):
        """Load session memory from file."""
        try:
            memory_file = Path("openai_session_memory.json")
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    self.session_memory = json.load(f)
                print(f"📂 Session memory loaded from {memory_file}")
                return True
        except Exception as e:
            print(f"❌ Error loading session memory: {e}")
        return False
    
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

    async def _execute_auto_workflow(self, query: str, max_emails: int, max_jobs: int) -> dict:
        """Execute complete automated job search workflow."""
        try:
            print(f"🔄 Starting auto workflow: {query}")
            
            # Step 1: Search emails
            emails = list_emails(query, max_emails)
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
                    urls = extract_job_urls(email['id'])
                    self.session_memory['job_urls'][email['id']] = urls
                    all_urls.extend([url_info['url'] for url_info in urls if 'url' in url_info])
                except Exception as e:
                    print(f"Failed to extract URLs from email {email['id']}: {e}")
            
            # Step 3: Scrape jobs (limit to max_jobs)
            urls_to_scrape = all_urls[:max_jobs]
            scraped_jobs = []
            
            from mcp_tools.scraper_tools import scrape_job_async
            for url in urls_to_scrape:
                try:
                    job_data = await scrape_job_async(url)
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


async def main():
    """Main chat interface for OpenAI LLM Host."""
    print("🚀 LinkedIn Job Assistant - OpenAI + MCP Integration")
    print("=" * 70)
    print("🎯 GPT-4 powered job search with MCP tools")
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
    
    # Initialize host
    try:
        host = OpenAILLMHost(api_key)
        print("✅ OpenAI LLM Host initialized successfully!")
        
        # Load previous session memory if available
        if host.load_session_memory():
            memory_summary = host.get_memory_summary()
            if memory_summary != "No data in memory":
                print(f"📂 Loaded previous session: {memory_summary}")
        
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
            
            # Process with OpenAI + MCP
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