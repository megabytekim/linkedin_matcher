#!/usr/bin/env python3
"""
LinkedIn Job Scraper MCP Server Launcher

This file starts the MCP server with all registered tools.
Import all tool modules to register them with the main app.
"""

# Import the main server app
from core.server_app import app

# Import all tool modules to register their tools
import core.tools.gmail
import core.tools.scraper
import core.tools.scraper_gmail

# Add a workflow tool
@app.tool()
def full_workflow(query: str = "from:linkedin.com", max_emails: int = 5, max_jobs: int = 10):
    """
    Complete workflow: Search emails → Extract URLs → Scrape jobs.
    
    Args:
        query: Gmail search query for finding job emails
        max_emails: Maximum emails to process
        max_jobs: Maximum jobs to scrape
        
    Returns:
        Dictionary with emails found, URLs extracted, and jobs scraped
    """
    from core.tools.gmail import list_emails, extract_job_urls
    from core.tools.scraper import scrape_job
    
    # Step 1: Find emails
    emails = list_emails(query, max_emails)
    
    # Step 2: Extract URLs from all emails
    all_urls = []
    for email in emails[:max_emails]:
        urls = extract_job_urls(email['id'])
        all_urls.extend([url_info['url'] for url_info in urls])
    
    # Step 3: Scrape jobs (limit to max_jobs)
    urls_to_scrape = all_urls[:max_jobs]
    job_results = []
    for url in urls_to_scrape:
        try:
            job_data = scrape_job(url)
            if job_data:
                job_results.append(job_data)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
    
    return {
        'emails_found': len(emails),
        'urls_extracted': len(all_urls),
        'jobs_scraped': len(job_results),
        'job_data': job_results,
        'summary': f"Found {len(emails)} emails, extracted {len(all_urls)} URLs, scraped {len(job_results)} jobs"
    }

if __name__ == "__main__":
    import sys
    import logging
    
    # Configure logging for MCP server
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Send logs to stderr to avoid interfering with stdio communication
    )
    
    logger = logging.getLogger(__name__)
    
    # Log server startup to stderr
    logger.info("🚀 LinkedIn Job Scraper MCP Server Starting...")
    logger.info("📧 Gmail Tools: mcp_list_emails, mcp_extract_job_urls, mcp_get_message_content, mcp_add_label")
    logger.info("🌐 Scraper Tools: mcp_scrape_job, mcp_scrape_multiple_jobs, mcp_convert_to_guest_url, mcp_validate_linkedin_url, mcp_get_job_summary")
    logger.info("🔄 Workflow Tools: full_workflow")
    logger.info("📡 Running in stdio mode for MCP client communication")
    
    # Run the MCP server in stdio mode
    try:
        app.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("🛑 MCP Server stopped by user")
    except Exception as e:
        logger.error(f"❌ MCP Server error: {e}")
        sys.exit(1) 