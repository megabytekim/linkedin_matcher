# LinkedIn Job Matcher

> **Milestone: v2.0.0 — MCP-Only, Claude Desktop Server**
>
> This project is now a pure Claude Desktop MCP server. Local/CLI mode is no longer supported. All usage is via MCP (stdio) for Claude Desktop or compatible MCP clients.

An AI-powered job search assistant that automatically finds, extracts, and analyzes LinkedIn job opportunities from your Gmail inbox using GPT-4 and advanced web scraping.

## 🚀 Features

- **AI-Powered Analysis**: GPT-4 processes natural language queries about job search
- **Gmail Integration**: Automatically searches and processes LinkedIn job alert emails  
- **LinkedIn Scraping**: Extracts complete job details from LinkedIn URLs
- **MCP Architecture**: Client-Server architecture via stdio communication
- **Smart Workflow**: Automated email → URL extraction → job scraping pipeline
- **Session Memory**: Maintains context across conversations
- **CI/CD Ready**: GitHub Actions for automated testing

## 🏗️ Architecture

### MCP Client-Server (stdio)
```
Claude Desktop ↔ MCP Client ↔ subprocess(stdio) ↔ MCP Server ↔ Tools
```

## 🛠️ Quick Start

### For Claude Desktop Users

1. **Install the MCP Server**:
   ```bash
   git clone <repository-url>
   cd linkedin_matcher
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   export OPENAI_API_KEY='sk-your-openai-key'
   ```

3. **Configure Claude Desktop**:
   ```bash
   mkdir -p ~/.config/claude-desktop/mcp-servers
   cp claude_desktop_config.json ~/.config/claude-desktop/mcp-servers/
   ```

4. **Restart Claude Desktop** and the `linkedin-job-scraper` server will be available.

### For Developers

```python
# Test the MCP server directly
python -m core.serve

# Run integration tests
python test_mcp_integration.py
```

## 📋 Usage Examples

With Claude Desktop, you can ask:

```
🗣️  Find data science jobs in my emails
🤖 I'll search your Gmail for data science job opportunities...

🗣️  What are the latest machine learning positions?
🤖 Let me look for machine learning jobs and scrape the details...

🗣️  Scrape and summarize the 5 most recent job postings
🤖 I'll find recent job emails, extract URLs, and provide summaries...
```

## 🔧 Advanced Usage

### Testing

```bash
# Run comprehensive integration tests
python test_mcp_integration.py

# Test individual components
python run_tests.py

# Test Gmail functionality
python gmail_module/test_email_display.py
```

### Manual MCP Server Testing

```bash
# Test MCP server directly
python -m core.serve

# Test with MCP client
python host/mcp_client.py
```

## 📁 Project Structure

```
linkedin_matcher/
├── core/
│   ├── serve.py              # MCP Server launcher (main entry point)
│   ├── server_app.py         # FastMCP application
│   └── tools/
│       ├── gmail.py          # Pure Gmail data extraction tools
│       ├── scraper.py        # Pure LinkedIn scraping tools
│       └── scraper_gmail.py  # Combined scraper+gmail integration tools
├── host/
│   ├── openai_host.py        # GPT-4 host (for testing)
│   └── mcp_client.py         # MCP Client for subprocess communication
├── scraper_module/           # Scraper components
│   ├── job_scraper.py        # Core scraping functionality
│   └── tools/                # Scraper integration tools
│       ├── __init__.py
│       └── gmail_scraper.py  # Gmail+scraper workflows
├── gmail_module/             # Gmail components
│   ├── gmail_api.py          # Gmail API interface
│   └── tests/                # Gmail-specific tests
├── test_mcp_integration.py   # Integration tests
├── run_tests.py              # Test runner
├── claude_desktop_config.json # Claude Desktop configuration
└── requirements.txt          # Dependencies
```

## 🧪 Testing

```bash
# Run all tests
python run_tests.py

# Test MCP integration
python test_mcp_integration.py

# Test Gmail functionality
python gmail_module/test_email_display.py
```

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-your-key      # Required
OPENAI_MODEL=gpt-4o             # Optional (default: gpt-4o)
```

### Gmail API Setup
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API
4. Create credentials (OAuth 2.0)
5. Download `credentials.json` to project root

## 🛠️ Tools Architecture

### Pure Data Extraction Tools
**Gmail Tools** (`core/tools/gmail.py`)
- `list_emails` - Search and list Gmail messages
- `extract_job_urls` - Extract LinkedIn URLs from emails
- `get_message_content` - Get full email content
- `add_label` - Apply labels to emails

### Pure Scraping Tools  
**Scraper Tools** (`core/tools/scraper.py`)
- `scrape_job` - Scrape single LinkedIn job posting
- `scrape_multiple_jobs` - Batch scrape multiple jobs
- `validate_job_url` - Validate LinkedIn job URLs

### Integrated Workflow Tools
**Scraper+Gmail Tools** (`core/tools/scraper_gmail.py`)
- `get_job_details_from_email` - Extract URLs from email + scrape
- `scrape_jobs_from_email_urls` - Scrape jobs with email context
- `scrape_jobs_from_url_list` - Batch scrape with optional context
- `process_linkedin_emails` - Full email workflow processing

## 🎯 Key Features

1. **MCP-Only Architecture**: Clean client-server separation
2. **Process Isolation**: MCP server runs in separate subprocess
3. **Network Boundary**: JSON-RPC communication protocol
4. **Resource Management**: Proper cleanup and lifecycle management
5. **Error Handling**: Robust error recovery and logging
6. **Claude Desktop Integration**: Seamless integration with Claude Desktop

## 🔮 Future Enhancements

- [ ] WebSocket-based MCP communication
- [ ] Multi-server MCP deployment
- [ ] Advanced job matching algorithms
- [ ] Email classification and labeling
- [ ] Job application tracking
- [ ] Calendar integration for interviews

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.