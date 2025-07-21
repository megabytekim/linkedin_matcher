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

# The full_workflow functionality is now properly handled by:
# - mcp_process_linkedin_emails (for complete email processing)
# - mcp_get_job_details_from_email (for single email workflow)
# - Individual tools can be chained by the LLM with working memory

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
    logger.info("🔄 Combined Tools: mcp_get_job_details_from_email, mcp_scrape_jobs_from_email_urls, mcp_scrape_jobs_from_url_list, mcp_process_linkedin_emails")
    logger.info("📡 Running in stdio mode for MCP client communication")
    
    # Run the MCP server in stdio mode
    try:
        app.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("🛑 MCP Server stopped by user")
    except Exception as e:
        logger.error(f"❌ MCP Server error: {e}")
        sys.exit(1) 