"""
LinkedIn Job Scraper MCP Server

Single FastMCP application that serves as the central MCP server.
All tools are registered here to avoid multiple server instances.
"""

from fastmcp import FastMCP

# Single source of truth for MCP server
app = FastMCP("LinkedIn Tools")

# This is the only FastMCP instance in the entire application
# All tools will be registered on this app instance 