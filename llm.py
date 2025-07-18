#!/usr/bin/env python3
"""
LinkedIn Job Scraper - LLM Chat Interface

This is the main chat interface for the LinkedIn Job Scraper project.
It provides natural language interaction with Gmail and LinkedIn scraping capabilities.

Features:
- Natural language job search queries
- Gmail integration for job email analysis
- LinkedIn job scraping with full content
- Intelligent workflow automation
- Interactive chat experience
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import our modules
from gmail_module.gmail_api import GmailAPI
from scraper_module.job_scraper import JobScraper, scrape_job_page, scrape_multiple_jobs


class LinkedInJobAssistant:
    """
    LLM-powered assistant for LinkedIn job searching and analysis.
    
    This class provides a natural language interface to:
    - Search Gmail for job-related emails
    - Extract and analyze LinkedIn job postings
    - Provide intelligent job recommendations
    - Automate the complete job search workflow
    """
    
    def __init__(self):
        """Initialize the LinkedIn Job Assistant."""
        self.gmail = None
        self.scraper = None
        self.conversation_history = []
        self.job_cache = {}  # Cache scraped jobs to avoid re-scraping
        
    def init_services(self):
        """Initialize Gmail and scraper services."""
        try:
            print("🔐 Initializing Gmail connection...")
            self.gmail = GmailAPI()
            print("✅ Gmail connected successfully!")
            
            print("🌐 Initializing LinkedIn scraper...")
            self.scraper = JobScraper(min_delay=2.0, max_delay=4.0)
            print("✅ Scraper ready!")
            
            return True
        except Exception as e:
            print(f"❌ Error initializing services: {e}")
            return False
    
    async def process_query(self, user_input: str) -> str:
        """
        Process a natural language query and return a helpful response.
        
        Args:
            user_input: User's natural language query
            
        Returns:
            Formatted response with job information
        """
        query_lower = user_input.lower()
        
        # Analyze the intent
        if any(keyword in query_lower for keyword in ['help', 'commands', 'what can you do']):
            return self._show_help()
        
        elif any(keyword in query_lower for keyword in ['find', 'search', 'look for', 'show me']):
            return await self._handle_job_search(user_input)
        
        elif any(keyword in query_lower for keyword in ['emails', 'gmail', 'inbox']):
            return await self._handle_email_query(user_input)
        
        elif any(keyword in query_lower for keyword in ['scrape', 'analyze', 'details']):
            return await self._handle_scraping_query(user_input)
        
        elif any(keyword in query_lower for keyword in ['workflow', 'complete', 'full process']):
            return await self._handle_workflow_query(user_input)
        
        else:
            # Default: treat as job search
            return await self._handle_job_search(user_input)
    
    async def _handle_job_search(self, query: str) -> str:
        """Handle job search queries."""
        try:
            # Extract search terms
            search_terms = self._extract_search_terms(query)
            gmail_query = f"from:linkedin.com {search_terms}"
            
            print(f"🔍 Searching Gmail for: {search_terms}")
            
            # Search emails
            emails = self.gmail.list_messages(query=gmail_query, max_results=10)
            
            if not emails:
                return f"❌ No job emails found for '{search_terms}'. Try a broader search or check your Gmail."
            
            print(f"📧 Found {len(emails)} relevant emails")
            
            # Extract URLs from emails
            all_urls = []
            for email in emails[:5]:  # Limit to first 5 emails
                urls = self.gmail.extract_job_urls(email['id'])
                for url_info in urls:
                    all_urls.append({
                        'url': url_info['url'],
                        'email_subject': email['subject'],
                        'email_date': email['date']
                    })
            
            if not all_urls:
                return f"📧 Found {len(emails)} emails but no job URLs. They might not contain LinkedIn job links."
            
            # Scrape top jobs
            results = []
            max_jobs = min(3, len(all_urls))  # Limit to 3 jobs
            
            print(f"🌐 Scraping top {max_jobs} jobs...")
            
            for i, url_info in enumerate(all_urls[:max_jobs]):
                url = url_info['url']
                
                # Check cache first
                if url in self.job_cache:
                    job_data = self.job_cache[url]
                    print(f"✅ Using cached data for job {i+1}")
                else:
                    job_data = scrape_job_page(url, max_content_length=3000)
                    if job_data:
                        self.job_cache[url] = job_data
                        print(f"✅ Scraped job {i+1}: {job_data.get('title', 'Unknown')}")
                    else:
                        print(f"❌ Failed to scrape job {i+1}")
                        continue
                
                if job_data:
                    job_data['email_context'] = {
                        'subject': url_info['email_subject'],
                        'date': url_info['email_date']
                    }
                    results.append(job_data)
            
            return self._format_job_results(results, search_terms)
            
        except Exception as e:
            return f"❌ Error processing job search: {e}"
    
    async def _handle_email_query(self, query: str) -> str:
        """Handle email-related queries."""
        try:
            emails = self.gmail.list_messages(query="from:linkedin.com", max_results=10)
            
            response = f"📧 **Your LinkedIn Email Summary**\n\n"
            response += f"Found {len(emails)} LinkedIn emails:\n\n"
            
            for i, email in enumerate(emails[:5], 1):
                response += f"{i}. **{email['subject'][:60]}...**\n"
                response += f"   From: {email['from']}\n"
                response += f"   Date: {email['date']}\n"
                response += f"   Preview: {email['snippet'][:100]}...\n\n"
            
            if len(emails) > 5:
                response += f"... and {len(emails) - 5} more emails\n\n"
            
            response += "💡 **Try asking:** 'Find data science jobs' or 'Search for remote engineering positions'"
            
            return response
            
        except Exception as e:
            return f"❌ Error accessing emails: {e}"
    
    async def _handle_scraping_query(self, query: str) -> str:
        """Handle job scraping queries."""
        # Look for URLs in the query
        urls = re.findall(r'https?://[^\s]+', query)
        
        if not urls:
            return "❌ No URLs found in your message. Please provide a LinkedIn job URL to scrape."
        
        url = urls[0]  # Use first URL
        
        try:
            print(f"🌐 Scraping job: {url[:60]}...")
            job_data = scrape_job_page(url, max_content_length=5000)
            
            if job_data:
                return self._format_single_job(job_data)
            else:
                return "❌ Failed to scrape the job. The URL might be invalid or the job may no longer exist."
                
        except Exception as e:
            return f"❌ Error scraping job: {e}"
    
    async def _handle_workflow_query(self, query: str) -> str:
        """Handle complete workflow queries."""
        try:
            print("🚀 Running complete job search workflow...")
            
            # Step 1: Get recent emails
            emails = self.gmail.list_messages(query="from:linkedin.com", max_results=8)
            
            # Step 2: Extract all URLs
            all_urls = []
            for email in emails:
                urls = self.gmail.extract_job_urls(email['id'])
                all_urls.extend([url_info['url'] for url_info in urls])
            
            # Step 3: Scrape jobs
            scraped_jobs = []
            max_jobs = min(5, len(all_urls))
            
            for url in all_urls[:max_jobs]:
                job_data = scrape_job_page(url, max_content_length=2000)
                if job_data:
                    scraped_jobs.append(job_data)
            
            # Step 4: Format results
            response = f"🔄 **Complete Workflow Results**\n\n"
            response += f"📧 Analyzed: {len(emails)} emails\n"
            response += f"🔗 Found: {len(all_urls)} job URLs\n"
            response += f"✅ Scraped: {len(scraped_jobs)} jobs successfully\n\n"
            
            if scraped_jobs:
                response += "🎯 **Top Job Opportunities:**\n\n"
                for i, job in enumerate(scraped_jobs[:3], 1):
                    response += f"{i}. **{job['title']}** at **{job['company']}**\n"
                    response += f"   📍 {job.get('location', 'Location not specified')}\n"
                    response += f"   📝 {len(job.get('description', ''))} characters of description\n"
                    response += f"   🔗 {job.get('guest_url', job.get('url', 'URL unavailable'))}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error running workflow: {e}"
    
    def _extract_search_terms(self, query: str) -> str:
        """Extract search terms from natural language query."""
        # Remove common question words
        stop_words = ['find', 'search', 'look', 'show', 'me', 'for', 'jobs', 'positions', 'opportunities']
        
        words = query.lower().split()
        search_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return ' '.join(search_terms)
    
    def _format_job_results(self, results: List[Dict], search_terms: str) -> str:
        """Format job search results for display."""
        if not results:
            return f"❌ No jobs found for '{search_terms}'. The URLs might be invalid or LinkedIn might be blocking requests."
        
        response = f"🎯 **Found {len(results)} Job{'s' if len(results) > 1 else ''} for '{search_terms}'**\n\n"
        
        for i, job in enumerate(results, 1):
            response += f"**{i}. {job['title']}**\n"
            response += f"🏢 **Company:** {job['company']}\n"
            response += f"📍 **Location:** {job.get('location', 'Not specified')}\n"
            
            # Show email context
            if 'email_context' in job:
                email_date = job['email_context']['date']
                response += f"📧 **From email:** {email_date}\n"
            
            # Show description preview
            desc = job.get('description', '')
            if desc:
                preview = desc[:300] + "..." if len(desc) > 300 else desc
                response += f"📝 **Description:** {preview}\n"
            
            response += f"🔗 **Apply:** {job.get('guest_url', job.get('url', 'URL unavailable'))}\n"
            response += f"⏰ **Scraped:** {job.get('scraped_at', 'Unknown time')}\n\n"
            response += "─" * 50 + "\n\n"
        
        response += "💡 **Need more details?** Ask me to 'scrape' a specific URL for the full job description!"
        
        return response
    
    def _format_single_job(self, job_data: Dict) -> str:
        """Format a single job for detailed display."""
        response = f"📋 **Job Details**\n\n"
        response += f"**Title:** {job_data['title']}\n"
        response += f"**Company:** {job_data['company']}\n"
        response += f"**Location:** {job_data.get('location', 'Not specified')}\n\n"
        
        # Job details
        if job_data.get('jobDetails'):
            response += f"**Details:** {', '.join(job_data['jobDetails'])}\n\n"
        
        # Full description
        desc = job_data.get('description', '')
        if desc:
            response += f"**Description ({len(desc)} characters):**\n"
            response += f"{desc}\n\n"
        
        response += f"**Apply:** {job_data.get('guest_url', job_data.get('url', 'URL unavailable'))}\n"
        response += f"**Scraped:** {job_data.get('scraped_at', 'Unknown time')}\n"
        
        return response
    
    def _show_help(self) -> str:
        """Show help information."""
        return """🤖 **LinkedIn Job Assistant - Help**

I can help you find and analyze LinkedIn job opportunities! Here's what you can ask:

**🔍 Job Search:**
- "Find data science jobs"
- "Search for remote engineering positions"
- "Look for marketing roles in tech companies"
- "Show me recent machine learning opportunities"

**📧 Email Analysis:**
- "Show my LinkedIn emails"
- "What job emails do I have?"
- "Check my Gmail for job opportunities"

**🌐 Job Scraping:**
- "Scrape this job: [URL]"
- "Analyze this LinkedIn posting: [URL]"
- "Get details for this job: [URL]"

**🔄 Complete Workflow:**
- "Run a complete job search"
- "Full workflow for recent opportunities"
- "Analyze all my job emails and scrape the best ones"

**💡 Pro Tips:**
- I search your Gmail for LinkedIn job emails automatically
- I can scrape LinkedIn jobs without you needing to log in
- I handle popup blocking and get full job descriptions
- I cache results to avoid re-scraping the same jobs

**Example Questions:**
- "Find remote Python developer jobs"
- "What are the latest AI engineering opportunities?"
- "Search for product manager roles at startups"

Just ask me naturally - I'll understand what you need! 🚀"""

    def save_conversation(self):
        """Save conversation history to file."""
        try:
            history_file = Path("conversation_history.json")
            with open(history_file, 'w') as f:
                json.dump(self.conversation_history, f, indent=2, default=str)
            print(f"💾 Conversation saved to {history_file}")
        except Exception as e:
            print(f"❌ Error saving conversation: {e}")


async def main():
    """Main chat interface."""
    print("🚀 LinkedIn Job Assistant")
    print("=" * 60)
    print("🎯 Your AI-powered job search companion")
    print("💬 Ask me to find jobs, analyze emails, or scrape LinkedIn postings")
    print("❓ Type 'help' for commands or 'quit' to exit")
    print("=" * 60)
    
    # Initialize assistant
    assistant = LinkedInJobAssistant()
    
    if not assistant.init_services():
        print("❌ Failed to initialize services. Please check your configuration.")
        return
    
    print("\n✅ Ready! Ask me anything about your job search...")
    print("💡 Try: 'Find data science jobs' or 'Show my LinkedIn emails'\n")
    
    while True:
        try:
            # Get user input
            user_input = input("🗣️  You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thanks for using LinkedIn Job Assistant!")
                assistant.save_conversation()
                break
            
            # Process query
            print("\n🤔 Thinking...")
            response = await assistant.process_query(user_input)
            
            # Display response
            print(f"\n🤖 Assistant:\n{response}\n")
            
            # Save to conversation history
            assistant.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': user_input,
                'assistant': response
            })
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using LinkedIn Job Assistant!")
            assistant.save_conversation()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.\n")


if __name__ == "__main__":
    # Run the chat interface
    asyncio.run(main()) 